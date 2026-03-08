from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..services import document_service
from .schemas import EditDocumentRequest, NewDocumentRequest

router = APIRouter()


def _format_thread(doc) -> dict:
    """Format document as Quip thread response."""
    return {
        "thread": {
            "id": doc.id,
            "title": doc.title,
            "type": doc.thread_class,
            "link": doc.link or f"/thread/{doc.id}",
            "created_usec": int(doc.created_at.timestamp() * 1_000_000) if doc.created_at else 0,
            "updated_usec": int(doc.updated_at.timestamp() * 1_000_000) if doc.updated_at else 0,
            "author_id": doc.creator_id or "",
            "sharing": {"folder_ids": [doc.folder_id] if doc.folder_id else []},
        },
        "html": doc.content_html or "",
    }


@router.get("/threads/recent")
async def get_recent_threads(
    count: int = 50,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    docs = await document_service.list_recent_documents(db, limit=count)
    return [_format_thread(d) for d in docs]


@router.get("/threads/{thread_id}")
async def get_thread(
    thread_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, thread_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Thread not found")
    return _format_thread(doc)


@router.post("/threads/new-document")
async def new_document(
    req: NewDocumentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.create_document(
        db,
        title=req.title,
        content_html=req.content,
        folder_id=req.folder_id,
        creator_id=user.id,
        content_type=req.type,
        thread_class=req.type,
    )
    return _format_thread(doc)


@router.post("/threads/edit-document")
async def edit_document(
    req: EditDocumentRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.update_document(
        db,
        doc_id=req.thread_id,
        title=req.title,
        content_html=req.content,
        folder_id=req.folder_id,
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Thread not found")
    return _format_thread(doc)


@router.post("/threads/{thread_id}/delete")
async def delete_thread(
    thread_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await document_service.delete_document(db, thread_id)
    return {"ok": True}
