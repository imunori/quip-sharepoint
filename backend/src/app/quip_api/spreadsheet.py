"""
Quip-compatible spreadsheet API.
Spreadsheets are stored as JSON in Document.content_html.
"""
import json

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..auth import get_current_user
from ..database import get_db
from ..models import User
from ..services import document_service

router = APIRouter()


class SpreadsheetData(BaseModel):
    headers: list[str] = []
    rows: list[list[str]] = []


class AddRowRequest(BaseModel):
    thread_id: str
    cells: list[str]


class EditCellRequest(BaseModel):
    thread_id: str
    row: int
    col: int
    value: str


def _parse_spreadsheet(content_html: str) -> SpreadsheetData:
    """Parse spreadsheet data from JSON stored in content_html."""
    if not content_html:
        return SpreadsheetData()
    try:
        data = json.loads(content_html)
        return SpreadsheetData(**data)
    except (json.JSONDecodeError, TypeError):
        return SpreadsheetData()


def _serialize_spreadsheet(data: SpreadsheetData) -> str:
    return json.dumps(data.model_dump(), ensure_ascii=False)


@router.post("/threads/new-spreadsheet")
async def new_spreadsheet(
    title: str = "Untitled Spreadsheet",
    headers: list[str] | None = None,
    folder_id: str | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    initial_data = SpreadsheetData(
        headers=headers or ["A", "B", "C", "D", "E"],
        rows=[],
    )
    doc = await document_service.create_document(
        db,
        title=title,
        content_html=_serialize_spreadsheet(initial_data),
        folder_id=folder_id,
        creator_id=user.id,
        content_type="spreadsheet",
        thread_class="spreadsheet",
    )
    return {
        "thread": {
            "id": doc.id,
            "title": doc.title,
            "type": "spreadsheet",
        },
        "spreadsheet": initial_data.model_dump(),
    }


@router.get("/threads/{thread_id}/spreadsheet")
async def get_spreadsheet(
    thread_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, thread_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Thread not found")
    data = _parse_spreadsheet(doc.content_html)
    return {
        "thread_id": doc.id,
        "title": doc.title,
        "spreadsheet": data.model_dump(),
    }


@router.post("/threads/spreadsheet/add-row")
async def add_row(
    req: AddRowRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, req.thread_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Thread not found")
    data = _parse_spreadsheet(doc.content_html)
    row = req.cells[:len(data.headers)] if data.headers else req.cells
    while len(row) < len(data.headers):
        row.append("")
    data.rows.append(row)
    await document_service.update_document(
        db, doc_id=req.thread_id, content_html=_serialize_spreadsheet(data)
    )
    return {"ok": True, "row_index": len(data.rows) - 1, "spreadsheet": data.model_dump()}


@router.post("/threads/spreadsheet/edit-cell")
async def edit_cell(
    req: EditCellRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, req.thread_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Thread not found")
    data = _parse_spreadsheet(doc.content_html)
    if req.row < 0 or req.row >= len(data.rows):
        raise HTTPException(status_code=400, detail="Row index out of range")
    if req.col < 0 or req.col >= len(data.headers):
        raise HTTPException(status_code=400, detail="Column index out of range")
    data.rows[req.row][req.col] = req.value
    await document_service.update_document(
        db, doc_id=req.thread_id, content_html=_serialize_spreadsheet(data)
    )
    return {"ok": True, "spreadsheet": data.model_dump()}


@router.post("/threads/spreadsheet/delete-row")
async def delete_row(
    thread_id: str,
    row_index: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, thread_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Thread not found")
    data = _parse_spreadsheet(doc.content_html)
    if 0 <= row_index < len(data.rows):
        data.rows.pop(row_index)
    await document_service.update_document(
        db, doc_id=thread_id, content_html=_serialize_spreadsheet(data)
    )
    return {"ok": True, "spreadsheet": data.model_dump()}


@router.post("/threads/spreadsheet/add-column")
async def add_column(
    thread_id: str,
    header: str = "New",
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    doc = await document_service.get_document(db, thread_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Thread not found")
    data = _parse_spreadsheet(doc.content_html)
    data.headers.append(header)
    for row in data.rows:
        row.append("")
    await document_service.update_document(
        db, doc_id=thread_id, content_html=_serialize_spreadsheet(data)
    )
    return {"ok": True, "spreadsheet": data.model_dump()}
