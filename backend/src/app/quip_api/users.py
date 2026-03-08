from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services import user_service

router = APIRouter()


@router.get("/users/current")
async def get_current_user(db: AsyncSession = Depends(get_db)):
    user = await user_service.get_or_create_default_user(db)
    return {
        "id": user.id,
        "name": user.name,
        "emails": [user.email],
        "profile_picture_url": user.profile_picture_url or "",
    }


@router.get("/users/{user_id}")
async def get_user(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "id": user.id,
        "name": user.name,
        "emails": [user.email],
        "profile_picture_url": user.profile_picture_url or "",
    }
