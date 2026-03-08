from fastapi import APIRouter

from ..config import SITE_DESCRIPTION, SITE_TITLE
from .schemas import sp_wrap

router = APIRouter()


@router.get("/web")
async def get_web():
    return sp_wrap(
        {
            "Title": SITE_TITLE,
            "Description": SITE_DESCRIPTION,
            "Url": "/",
            "ServerRelativeUrl": "/",
            "Created": "2024-01-01T00:00:00Z",
            "Id": "00000000-0000-0000-0000-000000000001",
        },
        metadata_type="SP.Web",
    )


@router.get("/web/title")
async def get_web_title():
    return sp_wrap({"Title": SITE_TITLE})


@router.post("/contextinfo")
async def get_context_info():
    return sp_wrap(
        {
            "FormDigestValue": "self-hosted-no-digest-needed",
            "FormDigestTimeoutSeconds": 1800,
        }
    )
