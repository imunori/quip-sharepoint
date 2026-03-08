"""JWT authentication middleware and utilities."""
from datetime import datetime, timedelta, timezone

import bcrypt as _bcrypt
import jwt
from fastapi import Depends, HTTPException, WebSocket, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from .config import JWT_ALGORITHM, JWT_EXPIRE_HOURS, JWT_SECRET
from .database import get_db
from .models import User
from .services import user_service

_bearer = HTTPBearer()


def hash_password(password: str) -> str:
    return _bcrypt.hashpw(password.encode(), _bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return _bcrypt.checkpw(password.encode(), hashed.encode())


def create_access_token(user_id: str, email: str) -> str:
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: AsyncSession = Depends(get_db),
) -> User:
    """FastAPI dependency: extract and verify JWT, return User."""
    payload = decode_token(credentials.credentials)
    user = await user_service.get_user(db, payload["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


async def get_ws_user(websocket: WebSocket, db: AsyncSession) -> User | None:
    """Extract user from WebSocket query param ?token=..."""
    token = websocket.query_params.get("token")
    if not token:
        return None
    try:
        payload = decode_token(token)
        return await user_service.get_user(db, payload["sub"])
    except HTTPException:
        return None
