from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services import document_service, user_service
from .schemas import MessageResponse, NewMessageRequest

router = APIRouter()


@router.get("/messages/{thread_id}")
async def get_messages(thread_id: str, db: AsyncSession = Depends(get_db)):
    messages = await document_service.get_messages(db, thread_id)
    return [
        {
            "id": m.id,
            "author_id": m.author_id,
            "text": m.text,
            "annotation_id": m.annotation_id,
            "created_usec": int(m.created_at.timestamp() * 1_000_000) if m.created_at else 0,
        }
        for m in messages
    ]


@router.post("/messages/new")
async def new_message(req: NewMessageRequest, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_or_create_default_user(db)
    msg = await document_service.create_message(
        db,
        doc_id=req.thread_id,
        author_id=user.id,
        text=req.content,
        annotation_id=req.annotation_id,
    )
    return {
        "id": msg.id,
        "author_id": msg.author_id,
        "text": msg.text,
        "annotation_id": msg.annotation_id,
        "created_usec": int(msg.created_at.timestamp() * 1_000_000) if msg.created_at else 0,
    }
