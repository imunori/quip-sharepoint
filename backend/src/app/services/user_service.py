from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import User, gen_id


async def get_user(db: AsyncSession, user_id: str) -> User | None:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, name: str, email: str) -> User:
    user = User(id=gen_id(), name=name, email=email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_default_user(db: AsyncSession) -> User:
    """Get or create default user for self-hosted setup."""
    user = await get_user_by_email(db, "admin@localhost")
    if not user:
        user = await create_user(db, "Admin", "admin@localhost")
    return user
