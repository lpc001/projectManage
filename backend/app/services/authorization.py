from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.authorization import (
    DataScopeType,
    Permission,
    PermissionType,
    Role,
    RoleDepartmentLink,
    RolePermissionLink,
    UserRoleLink,
)
from app.models.system import User


@dataclass(frozen=True)
class AuthorizationContext:
    role_codes: set[str]
    permission_codes: set[str]
    menu_permission_codes: set[str]
    action_permission_codes: set[str]
    api_permission_codes: set[str]
    data_scope_types: set[DataScopeType]
    custom_department_ids: set[int]

    @property
    def has_all_data_scope(self) -> bool:
        return DataScopeType.ALL in self.data_scope_types

    def has_permission(self, code: str) -> bool:
        return code in self.permission_codes


def build_authorization_context(db: Session, user: User) -> AuthorizationContext:
    roles = db.scalars(
        select(Role)
        .join(UserRoleLink, UserRoleLink.role_id == Role.id)
        .where(UserRoleLink.user_id == user.id, Role.is_active.is_(True))
    ).unique().all()
    role_ids = [role.id for role in roles]
    if not role_ids:
        return AuthorizationContext(set(), set(), set(), set(), set(), set(), set())

    permissions = db.scalars(
        select(Permission)
        .join(RolePermissionLink, RolePermissionLink.permission_id == Permission.id)
        .where(RolePermissionLink.role_id.in_(role_ids), Permission.is_active.is_(True))
    ).unique().all()
    custom_department_ids = set(
        db.scalars(
            select(RoleDepartmentLink.department_id).where(RoleDepartmentLink.role_id.in_(role_ids))
        ).all()
    )
    permission_codes = {permission.code for permission in permissions}
    return AuthorizationContext(
        role_codes={role.code for role in roles},
        permission_codes=permission_codes,
        menu_permission_codes={permission.code for permission in permissions if permission.permission_type == PermissionType.MENU},
        action_permission_codes={permission.code for permission in permissions if permission.permission_type == PermissionType.ACTION},
        api_permission_codes={permission.code for permission in permissions if permission.permission_type == PermissionType.API},
        data_scope_types={role.data_scope for role in roles},
        custom_department_ids=custom_department_ids,
    )

