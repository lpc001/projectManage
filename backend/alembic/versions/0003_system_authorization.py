"""add database-driven system authorization

Revision ID: 0003_system_authorization
Revises: 0002_projects
Create Date: 2026-11-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_system_authorization"
down_revision: Union[str, None] = "0002_projects"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROLE_ROWS = [
    {"code": "platform_admin", "name": "平台管理员", "description": "维护平台系统配置", "is_builtin": True, "is_active": True, "data_scope": "all"},
    {"code": "boss", "name": "老板", "description": "查看全局项目管理信息", "is_builtin": True, "is_active": True, "data_scope": "all"},
    {"code": "department_head", "name": "部门负责人", "description": "查看和管理所属部门项目", "is_builtin": True, "is_active": True, "data_scope": "department"},
    {"code": "pmo", "name": "PMO", "description": "维护项目台账和管理规则", "is_builtin": True, "is_active": True, "data_scope": "all"},
    {"code": "project_manager", "name": "项目经理", "description": "维护负责项目", "is_builtin": True, "is_active": True, "data_scope": "owned"},
    {"code": "member", "name": "项目成员", "description": "查看参与项目", "is_builtin": True, "is_active": True, "data_scope": "member"},
]


PERMISSION_ROWS = [
    {"code": "system:user:menu", "name": "用户管理菜单", "permission_type": "menu", "route_path": "/system/users", "sort_order": 10},
    {"code": "system:user:list", "name": "查看用户", "permission_type": "api", "http_method": "GET", "api_path": "/api/system-admin/users", "sort_order": 11},
    {"code": "system:user:create", "name": "新建用户", "permission_type": "action", "sort_order": 12},
    {"code": "system:user:update", "name": "编辑用户", "permission_type": "action", "sort_order": 13},
    {"code": "system:user:disable", "name": "启停用户", "permission_type": "action", "sort_order": 14},
    {"code": "system:role:menu", "name": "角色管理菜单", "permission_type": "menu", "route_path": "/system/roles", "sort_order": 20},
    {"code": "system:role:list", "name": "查看角色", "permission_type": "api", "http_method": "GET", "api_path": "/api/system-admin/roles", "sort_order": 21},
    {"code": "system:role:create", "name": "新建角色", "permission_type": "action", "sort_order": 22},
    {"code": "system:role:update", "name": "编辑角色", "permission_type": "action", "sort_order": 23},
    {"code": "system:permission:menu", "name": "权限目录菜单", "permission_type": "menu", "route_path": "/system/permissions", "sort_order": 30},
    {"code": "system:permission:list", "name": "查看权限目录", "permission_type": "api", "http_method": "GET", "api_path": "/api/system-admin/permissions", "sort_order": 31},
    {"code": "system:permission:update", "name": "编辑权限目录", "permission_type": "action", "sort_order": 32},
    {"code": "system:department:menu", "name": "部门管理菜单", "permission_type": "menu", "route_path": "/system/departments", "sort_order": 40},
    {"code": "system:department:list", "name": "查看部门", "permission_type": "api", "http_method": "GET", "api_path": "/api/system-admin/departments", "sort_order": 41},
    {"code": "system:department:update", "name": "编辑部门", "permission_type": "action", "sort_order": 42},
    {"code": "system:department:lookup", "name": "读取部门选项", "permission_type": "api", "http_method": "GET", "api_path": "/api/system/departments", "sort_order": 43},
    {"code": "system:user:lookup", "name": "读取用户选项", "permission_type": "api", "http_method": "GET", "api_path": "/api/system/users", "sort_order": 15},
    {"code": "system:audit:menu", "name": "操作审计菜单", "permission_type": "menu", "route_path": "/system/audit", "sort_order": 50},
    {"code": "system:audit:list", "name": "查看操作审计", "permission_type": "api", "http_method": "GET", "api_path": "/api/system-admin/audit", "sort_order": 51},
    {"code": "project:menu", "name": "项目台账菜单", "permission_type": "menu", "route_path": "/projects", "sort_order": 100},
    {"code": "project:list", "name": "查看项目", "permission_type": "api", "http_method": "GET", "api_path": "/api/projects", "sort_order": 101},
    {"code": "project:create", "name": "创建项目", "permission_type": "action", "sort_order": 102},
    {"code": "project:update", "name": "编辑项目", "permission_type": "action", "sort_order": 103},
    {"code": "project:archive", "name": "归档项目", "permission_type": "action", "sort_order": 104},
]


def upgrade() -> None:
    op.add_column("sys_user", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))

    op.create_table(
        "sys_role",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("data_scope", sa.String(length=30), nullable=False, server_default="member"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("code", name="uq_sys_role_code"),
        sa.CheckConstraint(
            "data_scope IN ('all', 'department', 'owned', 'member', 'custom_department')",
            name="ck_sys_role_data_scope",
        ),
    )
    op.create_index("ix_sys_role_code", "sys_role", ["code"], unique=False)

    op.create_table(
        "sys_permission",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("permission_type", sa.String(length=20), nullable=False),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("route_path", sa.String(length=200), nullable=True),
        sa.Column("http_method", sa.String(length=20), nullable=True),
        sa.Column("api_path", sa.String(length=300), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["parent_id"], ["sys_permission.id"], name="fk_sys_permission_parent"),
        sa.UniqueConstraint("code", name="uq_sys_permission_code"),
        sa.CheckConstraint("permission_type IN ('menu', 'action', 'api')", name="ck_sys_permission_type"),
    )
    op.create_index("ix_sys_permission_code", "sys_permission", ["code"], unique=False)

    op.create_table(
        "sys_user_role",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["sys_user.id"], name="fk_sys_user_role_user", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["sys_role.id"], name="fk_sys_user_role_role", ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "role_id", name="uq_sys_user_role"),
    )

    op.create_table(
        "sys_role_permission",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["role_id"], ["sys_role.id"], name="fk_sys_role_permission_role", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["permission_id"], ["sys_permission.id"], name="fk_sys_role_permission_permission", ondelete="CASCADE"),
        sa.UniqueConstraint("role_id", "permission_id", name="uq_sys_role_permission"),
    )

    op.create_table(
        "sys_role_department",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["role_id"], ["sys_role.id"], name="fk_sys_role_department_role", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["department_id"], ["sys_department.id"], name="fk_sys_role_department_department", ondelete="CASCADE"),
        sa.UniqueConstraint("role_id", "department_id", name="uq_sys_role_department"),
    )

    op.create_table(
        "sys_audit_log",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("module", sa.String(length=80), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("target_type", sa.String(length=80), nullable=True),
        sa.Column("target_id", sa.String(length=80), nullable=True),
        sa.Column("request_method", sa.String(length=20), nullable=True),
        sa.Column("request_path", sa.String(length=300), nullable=True),
        sa.Column("result", sa.String(length=20), nullable=False),
        sa.Column("summary", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["sys_user.id"], name="fk_sys_audit_log_user"),
    )

    role_table = sa.table(
        "sys_role",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("is_builtin", sa.Boolean),
        sa.column("is_active", sa.Boolean),
        sa.column("data_scope", sa.String),
    )
    op.bulk_insert(role_table, ROLE_ROWS)

    permission_table = sa.table(
        "sys_permission",
        sa.column("code", sa.String),
        sa.column("name", sa.String),
        sa.column("permission_type", sa.String),
        sa.column("route_path", sa.String),
        sa.column("http_method", sa.String),
        sa.column("api_path", sa.String),
        sa.column("sort_order", sa.Integer),
        sa.column("is_builtin", sa.Boolean),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        permission_table,
        [
            {
                "code": row["code"],
                "name": row["name"],
                "permission_type": row["permission_type"],
                "route_path": row.get("route_path"),
                "http_method": row.get("http_method"),
                "api_path": row.get("api_path"),
                "sort_order": row["sort_order"],
                "is_builtin": True,
                "is_active": True,
            }
            for row in PERMISSION_ROWS
        ],
    )

    connection = op.get_bind()
    role_ids = dict(connection.execute(sa.text("SELECT code, id FROM sys_role")).fetchall())
    permission_ids = dict(connection.execute(sa.text("SELECT code, id FROM sys_permission")).fetchall())

    platform_permissions = [{"role_id": role_ids["platform_admin"], "permission_id": permission_id} for permission_id in permission_ids.values()]
    project_permissions = {
        "boss": ["project:menu", "project:list"],
        "department_head": ["project:menu", "project:list", "project:update", "system:department:lookup", "system:user:lookup"],
        "pmo": ["project:menu", "project:list", "project:create", "project:update", "project:archive", "system:department:lookup", "system:user:lookup"],
        "project_manager": ["project:menu", "project:list", "project:update", "system:department:lookup", "system:user:lookup"],
        "member": ["project:menu", "project:list"],
    }
    business_permissions = [
        {"role_id": role_ids[role_code], "permission_id": permission_ids[permission_code]}
        for role_code, permission_codes in project_permissions.items()
        for permission_code in permission_codes
    ]
    connection.execute(
        sa.text(
            "INSERT INTO sys_role_permission (role_id, permission_id) VALUES (:role_id, :permission_id)"
        ),
        platform_permissions + business_permissions,
    )

    legacy_users = connection.execute(sa.text("SELECT id, role FROM sys_user")).fetchall()
    legacy_links = [
        {"user_id": user_id, "role_id": role_ids[legacy_role]}
        for user_id, legacy_role in legacy_users
    ]
    if legacy_links:
        connection.execute(
            sa.text("INSERT INTO sys_user_role (user_id, role_id) VALUES (:user_id, :role_id)"),
            legacy_links,
        )


def downgrade() -> None:
    op.drop_table("sys_audit_log")
    op.drop_table("sys_role_department")
    op.drop_table("sys_role_permission")
    op.drop_table("sys_user_role")
    op.drop_index("ix_sys_permission_code", table_name="sys_permission")
    op.drop_table("sys_permission")
    op.drop_index("ix_sys_role_code", table_name="sys_role")
    op.drop_table("sys_role")
    op.drop_column("sys_user", "token_version")

