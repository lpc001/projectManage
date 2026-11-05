"""remove legacy single-role authorization column

Revision ID: 0004_remove_legacy_role
Revises: 0003_system_authorization
Create Date: 2026-11-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_remove_legacy_role"
down_revision: Union[str, None] = "0003_system_authorization"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("ck_sys_user_role", "sys_user", type_="check")
    op.drop_column("sys_user", "role")


def downgrade() -> None:
    op.add_column("sys_user", sa.Column("role", sa.String(length=19), nullable=True))
    op.create_check_constraint(
        "ck_sys_user_role",
        "sys_user",
        "role IN ('boss', 'department_head', 'pmo', 'project_manager', 'member')",
    )

