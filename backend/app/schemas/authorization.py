from pydantic import BaseModel, ConfigDict

from app.models.authorization import DataScopeType, PermissionType


class RoleCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    data_scope: DataScopeType = DataScopeType.MEMBER


class RoleUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None
    data_scope: DataScopeType | None = None


class RoleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    description: str | None
    is_builtin: bool
    is_active: bool
    data_scope: DataScopeType
    permission_ids: list[int]


class PermissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    permission_type: PermissionType
    parent_id: int | None
    route_path: str | None
    http_method: str | None
    api_path: str | None
    sort_order: int
    is_builtin: bool
    is_active: bool


class RolePermissionUpdate(BaseModel):
    permission_ids: list[int]


class RoleDataScopeUpdate(BaseModel):
    data_scope: DataScopeType
    department_ids: list[int] = []

