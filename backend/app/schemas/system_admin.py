from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.auth import RoleSummary


class AdminUserCreate(BaseModel):
    username: str
    display_name: str
    password: str = Field(min_length=8)
    department_id: int
    role_ids: list[int] = []


class AdminUserUpdate(BaseModel):
    display_name: str | None = None
    department_id: int | None = None
    is_active: bool | None = None


class AdminUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    department_id: int
    is_active: bool
    roles: list[RoleSummary]
    created_at: datetime
    updated_at: datetime


class DepartmentCreate(BaseModel):
    name: str
    code: str
    parent_id: int | None = None


class DepartmentUpdate(BaseModel):
    name: str | None = None
    parent_id: int | None = None
    is_active: bool | None = None


class DepartmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    parent_id: int | None
    is_active: bool


class AuditResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    module: str
    action: str
    target_type: str | None
    target_id: str | None
    result: str
    summary: str | None
    created_at: datetime

