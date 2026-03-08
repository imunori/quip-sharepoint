from fastapi import APIRouter

from . import files, lists, web

router = APIRouter(prefix="/_api")
router.include_router(web.router)
router.include_router(lists.router)
router.include_router(files.router)
