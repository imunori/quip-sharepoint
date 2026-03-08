"""Authentication endpoints: register, login, me."""
import logging
import os

import boto3
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import create_access_token, get_current_user, hash_password, verify_password
from .database import get_db
from .models import User
from .services import user_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])

# SNS notification for new registrations
_sns_topic_arn = os.environ.get("REGISTRATION_SNS_TOPIC_ARN")
_sns_client = None


def _get_sns_client():
    global _sns_client
    if _sns_client is None:
        _sns_client = boto3.client("sns", region_name=os.environ.get("AWS_REGION", "ap-northeast-1"))
    return _sns_client


def _notify_registration(name: str, email: str, ip: str):
    """Send SNS notification for new user registration."""
    if not _sns_topic_arn:
        return
    try:
        _get_sns_client().publish(
            TopicArn=_sns_topic_arn,
            Subject="[Quip-SharePoint] New user registered",
            Message=f"New user registered:\n\nName: {name}\nEmail: {email}\nIP: {ip}\n",
        )
    except Exception as e:
        logger.warning(f"Failed to send SNS notification: {e}")


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, request: Request, db: AsyncSession = Depends(get_db)):
    existing = await user_service.get_user_by_email(db, req.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    user = await user_service.create_user(
        db, name=req.name, email=req.email, password_hash=hash_password(req.password)
    )
    token = create_access_token(user.id, user.email)

    # Log and notify
    client_ip = request.client.host if request.client else "unknown"
    logger.info(f"NEW_USER_REGISTERED: name={req.name}, email={req.email}, ip={client_ip}, user_id={user.id}")
    _notify_registration(req.name, req.email, client_ip)

    return TokenResponse(
        access_token=token,
        user={"id": user.id, "name": user.name, "email": user.email},
    )


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    user = await user_service.get_user_by_email(db, req.email)
    if not user or not user.password_hash:
        logger.warning(f"LOGIN_FAILED: email={req.email}, ip={client_ip}, reason=user_not_found")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not verify_password(req.password, user.password_hash):
        logger.warning(f"LOGIN_FAILED: email={req.email}, ip={client_ip}, reason=wrong_password")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    logger.info(f"LOGIN_SUCCESS: email={req.email}, ip={client_ip}, user_id={user.id}")
    token = create_access_token(user.id, user.email)
    return TokenResponse(
        access_token=token,
        user={"id": user.id, "name": user.name, "email": user.email},
    )


@router.get("/me")
async def me(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "profile_picture_url": user.profile_picture_url or "",
    }
