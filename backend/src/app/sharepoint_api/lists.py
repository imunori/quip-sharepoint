from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_db
from ..services import document_service, folder_service, user_service
from .schemas import sp_wrap, sp_wrap_collection

router = APIRouter()


def _folder_to_sp_list(folder, item_count: int = 0) -> dict:
    return {
        "Id": folder.id,
        "Title": folder.title,
        "Description": "",
        "ItemCount": item_count,
        "BaseTemplate": 101 if folder.folder_type == "document_library" else 100,
        "Created": folder.created_at.isoformat() if folder.created_at else "",
        "LastItemModifiedDate": folder.updated_at.isoformat() if folder.updated_at else "",
        "ParentWebUrl": "/",
    }


def _doc_to_sp_item(doc) -> dict:
    return {
        "Id": doc.id,
        "Title": doc.title,
        "ContentType": doc.content_type,
        "Created": doc.created_at.isoformat() if doc.created_at else "",
        "Modified": doc.updated_at.isoformat() if doc.updated_at else "",
        "AuthorId": doc.creator_id or "",
        "FileSystemObjectType": 0,  # 0=file, 1=folder
        "ServerRelativeUrl": doc.file_path or f"/{doc.id}",
    }


@router.get("/web/lists")
async def get_lists(db: AsyncSession = Depends(get_db)):
    folders = await folder_service.list_folders(db)
    items = [_folder_to_sp_list(f) for f in folders]
    return sp_wrap_collection(items, metadata_type="SP.List")


@router.post("/web/lists")
async def create_list(request: Request, db: AsyncSession = Depends(get_db)):
    body = await request.json()
    user = await user_service.get_or_create_default_user(db)
    base_template = body.get("BaseTemplate", 100)
    folder_type = "document_library" if base_template == 101 else "list"
    folder = await folder_service.create_folder(
        db,
        title=body.get("Title", "New List"),
        creator_id=user.id,
        folder_type=folder_type,
    )
    return sp_wrap(_folder_to_sp_list(folder), metadata_type="SP.List")


@router.get("/web/lists/getbytitle('{title}')")
async def get_list_by_title(title: str, db: AsyncSession = Depends(get_db)):
    folder = await folder_service.get_folder_by_title(db, title)
    if not folder:
        raise HTTPException(status_code=404, detail=f"List '{title}' not found")
    return sp_wrap(_folder_to_sp_list(folder), metadata_type="SP.List")


@router.get("/web/lists/getbytitle('{title}')/items")
async def get_list_items(title: str, db: AsyncSession = Depends(get_db)):
    folder = await folder_service.get_folder_by_title(db, title)
    if not folder:
        raise HTTPException(status_code=404, detail=f"List '{title}' not found")
    docs = await folder_service.get_folder_documents(db, folder.id)
    items = [_doc_to_sp_item(d) for d in docs]
    return sp_wrap_collection(items, metadata_type="SP.Data.ListItem")


@router.post("/web/lists/getbytitle('{title}')/items")
async def create_list_item(title: str, request: Request, db: AsyncSession = Depends(get_db)):
    folder = await folder_service.get_folder_by_title(db, title)
    if not folder:
        raise HTTPException(status_code=404, detail=f"List '{title}' not found")
    body = await request.json()
    user = await user_service.get_or_create_default_user(db)
    doc = await document_service.create_document(
        db,
        title=body.get("Title", "New Item"),
        content_html=body.get("Content", ""),
        folder_id=folder.id,
        creator_id=user.id,
        content_type="list_item" if folder.folder_type == "list" else "document",
    )
    return sp_wrap(_doc_to_sp_item(doc), metadata_type="SP.Data.ListItem")


@router.get("/web/lists/getbytitle('{title}')/items({item_id})")
async def get_list_item(title: str, item_id: str, db: AsyncSession = Depends(get_db)):
    doc = await document_service.get_document(db, item_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    return sp_wrap(_doc_to_sp_item(doc), metadata_type="SP.Data.ListItem")


@router.put("/web/lists/getbytitle('{title}')/items({item_id})")
@router.post("/web/lists/getbytitle('{title}')/items({item_id})")
async def update_list_item(
    title: str, item_id: str, request: Request, db: AsyncSession = Depends(get_db)
):
    body = await request.json()
    doc = await document_service.update_document(
        db,
        doc_id=item_id,
        title=body.get("Title"),
        content_html=body.get("Content"),
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Item not found")
    return sp_wrap(_doc_to_sp_item(doc), metadata_type="SP.Data.ListItem")


@router.delete("/web/lists/getbytitle('{title}')/items({item_id})")
async def delete_list_item(title: str, item_id: str, db: AsyncSession = Depends(get_db)):
    await document_service.delete_document(db, item_id)
    return {"ok": True}
