from typing import Optional

from pydantic import BaseModel, Field


class WorkEvidenceResponse(BaseModel):
    id: int
    subfolder_id: int
    evidence_type: str
    name: str
    progress_percent: float
    url: Optional[str] = None
    file_name: Optional[str] = None
    file_url: Optional[str] = None
    order_index: int
    group_id: Optional[int] = None


class WorkSubfolderResponse(BaseModel):
    id: int
    project_id: int
    name: str
    order_index: int
    progress_percent: float = 0
    evidences: list[WorkEvidenceResponse] = Field(default_factory=list)


class WorkFolderResponse(BaseModel):
    id: int
    name: str
    order_index: int


class WorkFolderCreate(BaseModel):
    name: str


class WorkFolderUpdate(BaseModel):
    name: Optional[str] = None


class WorkProjectResponse(BaseModel):
    id: int
    name: str
    folder_id: int
    folder_name: str
    logo_url: Optional[str] = None
    order_index: int
    progress_percent: float = 0
    subfolders: list[WorkSubfolderResponse] = Field(default_factory=list)


class WorkProjectCreate(BaseModel):
    name: str
    folder_id: int


class WorkProjectUpdate(BaseModel):
    name: Optional[str] = None
    folder_id: Optional[int] = None


class WorkSubfolderCreate(BaseModel):
    name: str


class WorkSubfolderUpdate(BaseModel):
    name: Optional[str] = None


class WorkEvidenceCreateJson(BaseModel):
    evidence_type: str
    name: str
    progress_percent: float = 0
    url: Optional[str] = None


class WorkEvidenceUpdate(BaseModel):
    name: Optional[str] = None
    progress_percent: Optional[float] = None
    url: Optional[str] = None
    group_id: Optional[int] = None


class ReorderItem(BaseModel):
    id: int
    order_index: int
    group_id: Optional[int] = None


class ReorderRequest(BaseModel):
    items: list[ReorderItem]
