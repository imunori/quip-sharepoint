from fastapi import APIRouter

from . import folders, messages, spreadsheet, threads, users

router = APIRouter(prefix="/api/1")
router.include_router(threads.router)
router.include_router(folders.router)
router.include_router(messages.router)
router.include_router(users.router)
router.include_router(spreadsheet.router)
