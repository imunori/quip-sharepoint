from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..services import user_service

router = APIRouter()


@router.get("/users/current")
async def get_current_user_endpoint(user: User = Depends(get_current_user)):
    return {
        "id": user.id,
        "name": user.name,
        "emails": [user.email],
        "profile_picture_url": user.profile_picture_url or "",
    }


@router.get("/users/{user_id}")
async def get_user(
    user_id: str,
    _current: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "name": user.name,
        "emails": [user.email],
        "profile_picture_url": user.profile_picture_url or "",
    }
