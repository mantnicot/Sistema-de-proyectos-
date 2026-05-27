from typing import Any, Optional

from pydantic import BaseModel, Field

from app.domain.entities import FieldType, UserRole


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: UserRole
    username: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRole


class FormFieldCreate(BaseModel):
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


class FormFieldUpdate(BaseModel):
    name: Optional[str] = None
    label: Optional[str] = None
    field_type: Optional[FieldType] = None
    placeholder: Optional[str] = None
    required: Optional[bool] = None
    order_index: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    max_length: Optional[int] = None
    list_options: Optional[list[str]] = None
    list_multiple: Optional[bool] = None
    section: Optional[str] = None


class FormFieldResponse(FormFieldCreate):
    id: int

    model_config = {"from_attributes": True}


class ReorderFieldsRequest(BaseModel):
    field_ids: list[int]


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    data: dict[str, Any] = Field(default_factory=dict)


class ProjectUpdate(ProjectCreate):
    pass


class ProjectResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    data: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str
    success: bool = True
