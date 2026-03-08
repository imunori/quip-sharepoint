from datetime import datetime

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    profile_picture_url: str = ""

    class Config:
        from_attributes = True


class MessageResponse(BaseModel):
    id: str
    author_id: str
    text: str
    annotation_id: str | None = None
    created_at: datetime

    class Config:
        from_attributes = True


class ThreadResponse(BaseModel):
    thread: dict
    html: str


class FolderResponse(BaseModel):
    folder: dict
    member_ids: list[str] = []
    children: list[dict] = []


class NewDocumentRequest(BaseModel):
    title: str = "Untitled"
    content: str = ""
    member_ids: list[str] = []
    folder_id: str | None = None
    type: str = "document"  # document, spreadsheet


class EditDocumentRequest(BaseModel):
    thread_id: str
    content: str | None = None
    title: str | None = None
    folder_id: str | None = None


class NewFolderRequest(BaseModel):
    title: str
    parent_id: str | None = None
    color: str = "manila"
    member_ids: list[str] = []


class UpdateFolderRequest(BaseModel):
    folder_id: str
    title: str | None = None
    color: str | None = None


class NewMessageRequest(BaseModel):
    thread_id: str
    content: str
    annotation_id: str | None = None
