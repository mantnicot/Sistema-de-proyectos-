from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WorkFolderCategory(str, Enum):
    POLUX = "POLUX"
    ACADEMICA = "ACADEMICA"


class EvidenceType(str, Enum):
    DOCUMENT = "document"
    URL = "url"


class WorkEvidence(BaseModel):
    id: Optional[int] = None
    subfolder_id: int
    evidence_type: EvidenceType
    name: str
    progress_percent: float = 0
    url: Optional[str] = None
    file_path: Optional[str] = None
    file_name: Optional[str] = None
    order_index: int = 0
    group_id: Optional[int] = None


class WorkSubfolder(BaseModel):
    id: Optional[int] = None
    project_id: int
    name: str
    order_index: int = 0


class WorkProject(BaseModel):
    id: Optional[int] = None
    name: str
    folder: WorkFolderCategory
    logo_path: Optional[str] = None
    order_index: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
