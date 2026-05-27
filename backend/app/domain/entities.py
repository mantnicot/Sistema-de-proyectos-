from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field


class UserRole(str, Enum):
    ADMIN = "admin"
    GENERAL = "general"


class FieldType(str, Enum):
    TEXT = "text"
    TEXTAREA = "textarea"
    INTEGER = "integer"
    DECIMAL = "decimal"
    PERCENTAGE = "percentage"
    TIME = "time"
    LIST = "list"
    IMAGE = "image"
    HYPERLINK = "hyperlink"


class User(BaseModel):
    id: Optional[int] = None
    username: str
    email: str
    role: UserRole
    is_active: bool = True
    created_at: Optional[datetime] = None


class FormField(BaseModel):
    id: Optional[int] = None
    name: str
    label: str
    field_type: FieldType
    placeholder: Optional[str] = None
    required: bool = False
    order_index: int = 0
    width: int = 100
    height: int = 1
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    max_length: Optional[int] = None
    list_options: list[str] = Field(default_factory=list)
    list_multiple: bool = False
    section: str = "general"


class Project(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[int] = None


class AuditLog(BaseModel):
    id: Optional[int] = None
    entity_type: str
    entity_id: int
    action: str
    user_id: Optional[int] = None
    details: Optional[str] = None
    created_at: Optional[datetime] = None
