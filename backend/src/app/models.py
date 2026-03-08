import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, LargeBinary, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


def gen_id() -> str:
    return uuid.uuid4().hex[:11]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=gen_id)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    profile_picture_url = Column(String, default="")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)


class Folder(Base):
    __tablename__ = "folders"

    id = Column(String, primary_key=True, default=gen_id)
    title = Column(String, nullable=False)
    parent_id = Column(String, ForeignKey("folders.id"), nullable=True)
    folder_type = Column(String, default="folder")  # folder, document_library, list
    color = Column(String, default="manila")
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)
    site_path = Column(String, default="")
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    children = relationship("Folder", backref="parent", remote_side="Folder.id", viewonly=True)
    documents = relationship("Document", back_populates="folder")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True, default=gen_id)
    title = Column(String, nullable=False, default="Untitled")
    content_html = Column(Text, default="")
    content_type = Column(String, default="document")  # document, spreadsheet, list_item
    folder_id = Column(String, ForeignKey("folders.id"), nullable=True)
    creator_id = Column(String, ForeignKey("users.id"), nullable=True)
    is_deleted = Column(Boolean, default=False)
    # Quip fields
    thread_class = Column(String, default="document")
    link = Column(String, default="")
    # SharePoint fields
    file_path = Column(String, default="")
    file_size = Column(Integer, default=0)
    mime_type = Column(String, default="text/html")
    # Yjs state
    yjs_state = Column(LargeBinary, nullable=True)

    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    folder = relationship("Folder", back_populates="documents")
    messages = relationship("Message", back_populates="document", order_by="Message.created_at")
    creator = relationship("User", foreign_keys=[creator_id])


class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=gen_id)
    document_id = Column(String, ForeignKey("documents.id"), nullable=False)
    author_id = Column(String, ForeignKey("users.id"), nullable=False)
    text = Column(Text, nullable=False)
    annotation_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=utcnow)

    document = relationship("Document", back_populates="messages")
    author = relationship("User", foreign_keys=[author_id])


class Attachment(Base):
    __tablename__ = "attachments"

    id = Column(String, primary_key=True, default=gen_id)
    document_id = Column(String, ForeignKey("documents.id"), nullable=True)
    folder_id = Column(String, ForeignKey("folders.id"), nullable=True)
    filename = Column(String, nullable=False)
    storage_path = Column(String, nullable=False)
    mime_type = Column(String, default="application/octet-stream")
    file_size = Column(Integer, default=0)
    uploader_id = Column(String, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=utcnow)


class FolderMember(Base):
    __tablename__ = "folder_members"

    folder_id = Column(String, ForeignKey("folders.id"), primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    role = Column(String, default="member")


class DocumentMember(Base):
    __tablename__ = "document_members"

    document_id = Column(String, ForeignKey("documents.id"), primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    role = Column(String, default="member")


class ListColumn(Base):
    __tablename__ = "list_columns"

    id = Column(String, primary_key=True, default=gen_id)
    folder_id = Column(String, ForeignKey("folders.id"), nullable=False)
    name = Column(String, nullable=False)
    field_type = Column(String, nullable=False, default="text")
    required = Column(Boolean, default=False)
    default_value = Column(String, nullable=True)
    choices = Column(Text, nullable=True)  # JSON array
    sort_order = Column(Integer, default=0)


class ListItemValue(Base):
    __tablename__ = "list_item_values"

    document_id = Column(String, ForeignKey("documents.id"), primary_key=True)
    column_id = Column(String, ForeignKey("list_columns.id"), primary_key=True)
    value = Column(Text, nullable=True)
