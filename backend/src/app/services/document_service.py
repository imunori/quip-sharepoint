from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Document, Folder, Message, gen_id, utcnow


async def list_recent_documents(db: AsyncSession, limit: int = 50) -> list[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.is_deleted == False)  # noqa: E712
        .order_by(Document.updated_at.desc())
        .limit(limit)
        .options(selectinload(Document.creator))
    )
    return list(result.scalars().all())


async def get_document(db: AsyncSession, doc_id: str) -> Document | None:
    result = await db.execute(
        select(Document)
        .where(Document.id == doc_id)
        .options(selectinload(Document.creator), selectinload(Document.messages))
    )
    return result.scalar_one_or_none()


async def create_document(
    db: AsyncSession,
    title: str,
    content_html: str = "",
    folder_id: str | None = None,
    creator_id: str | None = None,
    content_type: str = "document",
    thread_class: str = "document",
) -> Document:
    doc = Document(
        id=gen_id(),
        title=title,
        content_html=content_html,
        folder_id=folder_id,
        creator_id=creator_id,
        content_type=content_type,
        thread_class=thread_class,
    )
    if folder_id:
        doc.file_path = f"/{folder_id}/{doc.id}"
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def update_document(
    db: AsyncSession,
    doc_id: str,
    title: str | None = None,
    content_html: str | None = None,
    folder_id: str | None = None,
) -> Document | None:
    values: dict = {"updated_at": utcnow()}
    if title is not None:
        values["title"] = title
    if content_html is not None:
        values["content_html"] = content_html
    if folder_id is not None:
        values["folder_id"] = folder_id
    await db.execute(update(Document).where(Document.id == doc_id).values(**values))
    await db.commit()
    return await get_document(db, doc_id)


async def delete_document(db: AsyncSession, doc_id: str) -> bool:
    await db.execute(
        update(Document).where(Document.id == doc_id).values(is_deleted=True, updated_at=utcnow())
    )
    await db.commit()
    return True


async def get_messages(db: AsyncSession, doc_id: str) -> list[Message]:
    result = await db.execute(
        select(Message)
        .where(Message.document_id == doc_id)
        .order_by(Message.created_at.asc())
    )
    return list(result.scalars().all())


async def create_message(
    db: AsyncSession,
    doc_id: str,
    author_id: str,
    text: str,
    annotation_id: str | None = None,
) -> Message:
    msg = Message(
        id=gen_id(),
        document_id=doc_id,
        author_id=author_id,
        text=text,
        annotation_id=annotation_id,
    )
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    return msg
