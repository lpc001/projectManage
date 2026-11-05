"""add password reset permission and group permissions by menu

Revision ID: 0005_system_permission_groups
Revises: 0004_remove_legacy_role
Create Date: 2026-11-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0005_system_permission_groups"
down_revision: Union[str, None] = "0004_remove_legacy_role"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    connection = op.get_bind()
    permission_exists = connection.execute(
        sa.text("SELECT id FROM sys_permission WHERE code = 'system:user:reset_password'")
    ).scalar()
    if permission_exists is None:
        permission_id = connection.execute(
            sa.text(
                """
                INSERT INTO sys_permission
                    (code, name, permission_type, sort_order, is_builtin, is_active, created_at, updated_at)
                VALUES
                    ('system:user:reset_password', '重置用户密码', 'action', 16, true, true, now(), now())
                RETURNING id
                """
            )
        ).scalar_one()
    else:
        permission_id = permission_exists

    platform_role_id = connection.execute(
        sa.text("SELECT id FROM sys_role WHERE code = 'platform_admin'")
    ).scalar_one()
    existing_link = connection.execute(
        sa.text(
            "SELECT 1 FROM sys_role_permission WHERE role_id = :role_id AND permission_id = :permission_id"
        ),
        {"role_id": platform_role_id, "permission_id": permission_id},
    ).scalar()
    if existing_link is None:
        connection.execute(
            sa.text(
                "INSERT INTO sys_role_permission (role_id, permission_id, created_at, updated_at) VALUES (:role_id, :permission_id, now(), now())"
            ),
            {"role_id": platform_role_id, "permission_id": permission_id},
        )

    menu_groups = {
        "system:user:menu": "system:user:",
        "system:role:menu": "system:role:",
        "system:permission:menu": "system:permission:",
        "system:department:menu": "system:department:",
        "system:audit:menu": "system:audit:",
        "project:menu": "project:",
    }
    for menu_code, prefix in menu_groups.items():
        menu_id = connection.execute(
            sa.text("SELECT id FROM sys_permission WHERE code = :code"),
            {"code": menu_code},
        ).scalar()
        if menu_id is not None:
            connection.execute(
                sa.text(
                    "UPDATE sys_permission SET parent_id = :menu_id WHERE code LIKE :prefix AND code <> :menu_code"
                ),
                {"menu_id": menu_id, "prefix": f"{prefix}%", "menu_code": menu_code},
            )


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "DELETE FROM sys_role_permission WHERE permission_id = (SELECT id FROM sys_permission WHERE code = 'system:user:reset_password')"
        )
    )
    connection.execute(sa.text("DELETE FROM sys_permission WHERE code = 'system:user:reset_password'"))
    connection.execute(sa.text("UPDATE sys_permission SET parent_id = NULL"))

