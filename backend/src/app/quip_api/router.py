from fastapi import APIRouter

from . import folders, messages, threads, users

router = APIRouter(prefix="/api/1")
router.include_router(threads.router)
router.include_router(folders.router)
router.include_router(messages.router)
router.include_router(users.router)
