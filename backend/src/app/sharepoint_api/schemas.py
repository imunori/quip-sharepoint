from pydantic import BaseModel


class SPListCreate(BaseModel):
    Title: str
    Description: str = ""
    BaseTemplate: int = 100  # 100=generic list, 101=document library
    AllowContentTypes: bool = True


class SPListItemCreate(BaseModel):
    Title: str = ""
    # Additional fields are passed as extra kwargs


class SPListItemUpdate(BaseModel):
    Title: str | None = None


class SPMetadata(BaseModel):
    type: str


class SPListCreateOData(BaseModel):
    __metadata: SPMetadata | None = None
    Title: str
    Description: str = ""
    BaseTemplate: int = 100
    AllowContentTypes: bool = True


def sp_wrap(data: dict, metadata_type: str = "") -> dict:
    """Wrap response in SharePoint OData format."""
    result = {"d": data}
    if metadata_type:
        result["d"]["__metadata"] = {"type": metadata_type}
    return result


def sp_wrap_collection(items: list[dict], metadata_type: str = "") -> dict:
    """Wrap collection response in SharePoint OData format."""
    if metadata_type:
        for item in items:
            item["__metadata"] = {"type": metadata_type}
    return {"d": {"results": items}}
