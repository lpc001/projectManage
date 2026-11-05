from enum import StrEnum

from sqlalchemy import Boolean, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class PermissionType(StrEnum):
    MENU = "menu"
    ACTION = "action"
    API = "api"


class DataScopeType(StrEnum):
    ALL = "all"
    DEPARTMENT = "department"
    OWNED = "owned"
    MEMBER = "member"
    CUSTOM_DEPARTMENT = "custom_department"


class Role(TimestampMixin, Base):
    __tablename__ = "sys_role"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_scope: Mapped[DataScopeType] = mapped_column(
        Enum(
            DataScopeType,
            name="data_scope_type",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda scope_enum: [scope.value for scope in scope_enum],
        ),
        nullable=False,
        default=DataScopeType.MEMBER,
    )

    user_links: Mapped[list["UserRoleLink"]] = relationship(back_populates="role", cascade="all, delete-orphan")
    permission_links: Mapped[list["RolePermissionLink"]] = relationship(back_populates="role", cascade="all, delete-orphan")
    department_links: Mapped[list["RoleDepartmentLink"]] = relationship(back_populates="role", cascade="all, delete-orphan")
    users: Mapped[list["User"]] = relationship(
        "User",
        secondary="sys_user_role",
        back_populates="roles",
        viewonly=True,
    )
    permissions: Mapped[list["Permission"]] = relationship(
        "Permission",
        secondary="sys_role_permission",
        back_populates="roles",
        viewonly=True,
    )


class Permission(TimestampMixin, Base):
    __tablename__ = "sys_permission"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    permission_type: Mapped[PermissionType] = mapped_column(
        Enum(
            PermissionType,
            name="permission_type",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda type_enum: [item.value for item in type_enum],
        ),
        nullable=False,
    )
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("sys_permission.id"))
    route_path: Mapped[str | None] = mapped_column(String(200))
    http_method: Mapped[str | None] = mapped_column(String(20))
    api_path: Mapped[str | None] = mapped_column(String(300))
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_builtin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    parent: Mapped["Permission | None"] = relationship(remote_side="Permission.id", back_populates="children")
    children: Mapped[list["Permission"]] = relationship(back_populates="parent")
    role_links: Mapped[list["RolePermissionLink"]] = relationship(back_populates="permission", cascade="all, delete-orphan")
    roles: Mapped[list[Role]] = relationship(
        "Role",
        secondary="sys_role_permission",
        back_populates="permissions",
        viewonly=True,
    )


class UserRoleLink(TimestampMixin, Base):
    __tablename__ = "sys_user_role"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_sys_user_role"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id", ondelete="CASCADE"), nullable=False)
    role_id: Mapped[int] = mapped_column(ForeignKey("sys_role.id", ondelete="CASCADE"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="role_links")
    role: Mapped[Role] = relationship(back_populates="user_links")


class RolePermissionLink(TimestampMixin, Base):
    __tablename__ = "sys_role_permission"
    __table_args__ = (UniqueConstraint("role_id", "permission_id", name="uq_sys_role_permission"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("sys_role.id", ondelete="CASCADE"), nullable=False)
    permission_id: Mapped[int] = mapped_column(ForeignKey("sys_permission.id", ondelete="CASCADE"), nullable=False)

    role: Mapped[Role] = relationship(back_populates="permission_links")
    permission: Mapped[Permission] = relationship(back_populates="role_links")


class RoleDepartmentLink(TimestampMixin, Base):
    __tablename__ = "sys_role_department"
    __table_args__ = (UniqueConstraint("role_id", "department_id", name="uq_sys_role_department"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    role_id: Mapped[int] = mapped_column(ForeignKey("sys_role.id", ondelete="CASCADE"), nullable=False)
    department_id: Mapped[int] = mapped_column(ForeignKey("sys_department.id", ondelete="CASCADE"), nullable=False)

    role: Mapped[Role] = relationship(back_populates="department_links")
    department = relationship("Department")


class AuditLog(TimestampMixin, Base):
    __tablename__ = "sys_audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("sys_user.id"))
    module: Mapped[str] = mapped_column(String(80), nullable=False)
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    target_type: Mapped[str | None] = mapped_column(String(80))
    target_id: Mapped[str | None] = mapped_column(String(80))
    request_method: Mapped[str | None] = mapped_column(String(20))
    request_path: Mapped[str | None] = mapped_column(String(300))
    result: Mapped[str] = mapped_column(String(20), nullable=False)
    summary: Mapped[str | None] = mapped_column(Text)

