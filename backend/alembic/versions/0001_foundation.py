"""create system users and departments

Revision ID: 0001_foundation
Revises:
Create Date: 2026-11-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0001_foundation"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "sys_department",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("code", name="uq_sys_department_code"),
    )
    op.create_index("ix_sys_department_code", "sys_department", ["code"], unique=False)

    op.create_table(
        "sys_user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(length=120), nullable=False),
        sa.Column("display_name", sa.String(length=100), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=19), nullable=False),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["department_id"], ["sys_department.id"], name="fk_sys_user_department"),
        sa.UniqueConstraint("username", name="uq_sys_user_username"),
        sa.CheckConstraint(
            "role IN ('boss', 'department_head', 'pmo', 'project_manager', 'member')",
            name="ck_sys_user_role",
        ),
    )
    op.create_index("ix_sys_user_username", "sys_user", ["username"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_sys_user_username", table_name="sys_user")
    op.drop_table("sys_user")
    op.drop_index("ix_sys_department_code", table_name="sys_department")
    op.drop_table("sys_department")

