from fastapi import APIRouter, Depends, HTTPException, Response, UploadFile, File
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import Attachment, Folder, User, gen_id
from ..services import file_storage, folder_service
from .schemas import sp_wrap, sp_wrap_collection

router = APIRouter()

# Max upload size: 50MB
MAX_UPLOAD_SIZE = 50 * 1024 * 1024


def _attachment_to_sp_file(att: Attachment) -> dict:
    return {
        "Name": att.filename,
        "ServerRelativeUrl": f"/{att.storage_path}",
        "Length": str(att.file_size),
        "MajorVersion": 1,
        "MinorVersion": 0,
        "TimeCreated": att.created_at.isoformat() if att.created_at else "",
        "TimeLastModified": att.created_at.isoformat() if att.created_at else "",
        "UniqueId": att.id,
    }


def _folder_to_sp_folder(folder: Folder) -> dict:
    return {
        "Name": folder.title,
        "ServerRelativeUrl": folder.site_path or f"/{folder.id}",
        "ItemCount": len(folder.documents) if folder.documents else 0,
        "Exists": True,
        "UniqueId": folder.id,
    }


@router.get("/web/getfolderbyserverrelativeurl('{url:path}')")
async def get_folder_by_url(
    url: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    folder_id = url.strip("/").split("/")[-1] if "/" in url else url.strip("/")
    folder = await folder_service.get_folder(db, folder_id)
    if not folder:
        raise HTTPException(status_code=404, detail="Folder not found")
    return sp_wrap(_folder_to_sp_folder(folder), metadata_type="SP.Folder")


@router.get("/web/getfolderbyserverrelativeurl('{url:path}')/files")
async def get_folder_files(
    url: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    folder_id = url.strip("/").split("/")[-1] if "/" in url else url.strip("/")
    result = await db.execute(
        select(Attachment).where(Attachment.folder_id == folder_id)
    )
    attachments = result.scalars().all()
    items = [_attachment_to_sp_file(a) for a in attachments]
    return sp_wrap_collection(items, metadata_type="SP.File")


@router.get("/web/getfilebyserverrelativeurl('{url:path}')")
async def get_file_by_url(
    url: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Attachment).where(Attachment.storage_path == url.strip("/"))
    )
    att = result.scalar_one_or_none()
    if not att:
        raise HTTPException(status_code=404, detail="File not found")
    return sp_wrap(_attachment_to_sp_file(att), metadata_type="SP.File")


@router.get("/web/getfilebyserverrelativeurl('{url:path}')/$value")
async def download_file(
    url: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Attachment).where(Attachment.storage_path == url.strip("/"))
    )
    att = result.scalar_one_or_none()
    if not att:
        raise HTTPException(status_code=404, detail="File not found")
    data = file_storage.read_file(att.storage_path)
    return Response(content=data, media_type=att.mime_type or "application/octet-stream")


@router.post("/web/getfolderbyserverrelativeurl('{url:path}')/files/add(overwrite=true,url='{filename}')")
async def upload_file(
    url: str,
    filename: str,
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    folder_id = url.strip("/").split("/")[-1] if "/" in url else url.strip("/")
    data = await file.read()
    if len(data) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=413, detail="File too large (max 50MB)")
    storage_path = file_storage.save_file(folder_id, filename, data)
    att = Attachment(
        id=gen_id(),
        folder_id=folder_id,
        filename=filename,
        storage_path=storage_path,
        mime_type=file.content_type or "application/octet-stream",
        file_size=len(data),
        uploader_id=user.id,
    )
    db.add(att)
    await db.commit()
    await db.refresh(att)
    return sp_wrap(_attachment_to_sp_file(att), metadata_type="SP.File")


@router.delete("/web/getfilebyserverrelativeurl('{url:path}')")
async def delete_file(
    url: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Attachment).where(Attachment.storage_path == url.strip("/"))
    )
    att = result.scalar_one_or_none()
    if not att:
        raise HTTPException(status_code=404, detail="File not found")
    file_storage.delete_file(att.storage_path)
    await db.delete(att)
    await db.commit()
    return {"ok": True}
