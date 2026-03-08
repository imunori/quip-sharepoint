from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services import folder_service, user_service
from .schemas import NewFolderRequest, UpdateFolderRequest

router = APIRouter()


def _format_folder(folder, children=None) -> dict:
    child_ids = []
    if children:
        child_ids = [
            {"folder_id": c.id} if hasattr(c, "folder_type") else {"thread_id": c.id}
            for c in children
        ]
    return {
        "folder": {
            "id": folder.id,
            "title": folder.title,
            "color": folder.color or "manila",
            "parent_id": folder.parent_id,
            "creator_id": folder.creator_id or "",
            "created_usec": int(folder.created_at.timestamp() * 1_000_000) if folder.created_at else 0,
            "updated_usec": int(folder.updated_at.timestamp() * 1_000_000) if folder.updated_at else 0,
        },
        "member_ids": [],
        "children": child_ids,
    }


@router.get("/folders")
async def list_folders(
    parent_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    folders = await folder_service.list_folders(db, parent_id=parent_id)
    return [_format_folder(f) for f in folders]


@router.get("/folders/{folder_id}")
async def get_folder(folder_id: str, db: AsyncSession = Depends(get_db)):
    folder = await folder_service.get_folder(db, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    # Get child folders and documents
    child_folders = await folder_service.list_folders(db, parent_id=folder_id)
    child_docs = await folder_service.get_folder_documents(db, folder_id)
    children = list(child_folders) + list(child_docs)
    return _format_folder(folder, children)


@router.post("/folders/new")
async def new_folder(req: NewFolderRequest, db: AsyncSession = Depends(get_db)):
    user = await user_service.get_or_create_default_user(db)
    folder = await folder_service.create_folder(
        db,
        title=req.title,
        parent_id=req.parent_id,
        creator_id=user.id,
        color=req.color,
    )
    return _format_folder(folder)


@router.post("/folders/update")
async def update_folder(req: UpdateFolderRequest, db: AsyncSession = Depends(get_db)):
    folder = await folder_service.update_folder(
        db,
        folder_id=req.folder_id,
        title=req.title,
        color=req.color,
    )
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return _format_folder(folder)
