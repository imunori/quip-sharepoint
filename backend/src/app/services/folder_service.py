from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models import Document, Folder, gen_id, utcnow


async def list_folders(db: AsyncSession, parent_id: str | None = None) -> list[Folder]:
    q = select(Folder).order_by(Folder.title)
    if parent_id:
        q = q.where(Folder.parent_id == parent_id)
    else:
        q = q.where(Folder.parent_id == None)  # noqa: E711
    result = await db.execute(q)
    return list(result.scalars().all())


async def get_folder(db: AsyncSession, folder_id: str) -> Folder | None:
    result = await db.execute(
        select(Folder)
        .where(Folder.id == folder_id)
        .options(selectinload(Folder.documents))
    )
    return result.scalar_one_or_none()


async def create_folder(
    db: AsyncSession,
    title: str,
    parent_id: str | None = None,
    creator_id: str | None = None,
    folder_type: str = "folder",
    color: str = "manila",
) -> Folder:
    folder = Folder(
        id=gen_id(),
        title=title,
        parent_id=parent_id,
        creator_id=creator_id,
        folder_type=folder_type,
        color=color,
    )
    db.add(folder)
    await db.commit()
    await db.refresh(folder)
    return folder


async def update_folder(
    db: AsyncSession,
    folder_id: str,
    title: str | None = None,
    color: str | None = None,
) -> Folder | None:
    values: dict = {"updated_at": utcnow()}
    if title is not None:
        values["title"] = title
    if color is not None:
        values["color"] = color
    await db.execute(update(Folder).where(Folder.id == folder_id).values(**values))
    await db.commit()
    return await get_folder(db, folder_id)


async def get_folder_by_title(db: AsyncSession, title: str) -> Folder | None:
    result = await db.execute(
        select(Folder)
        .where(Folder.title == title)
        .options(selectinload(Folder.documents))
    )
    return result.scalar_one_or_none()


async def get_folder_documents(db: AsyncSession, folder_id: str) -> list[Document]:
    result = await db.execute(
        select(Document)
        .where(Document.folder_id == folder_id, Document.is_deleted == False)  # noqa: E712
        .order_by(Document.updated_at.desc())
    )
    return list(result.scalars().all())
