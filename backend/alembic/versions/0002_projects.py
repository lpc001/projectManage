"""create project register tables

Revision ID: 0002_projects
Revises: 0001_foundation
Create Date: 2026-11-05
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0002_projects"
down_revision: Union[str, None] = "0001_foundation"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pm_project",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("department_id", sa.Integer(), nullable=False),
        sa.Column("project_manager_id", sa.Integer(), nullable=False),
        sa.Column("client_name", sa.String(length=200), nullable=True),
        sa.Column("region", sa.String(length=100), nullable=True),
        sa.Column("planned_start_date", sa.Date(), nullable=False),
        sa.Column("planned_end_date", sa.Date(), nullable=False),
        sa.Column("lifecycle_status", sa.String(length=20), nullable=False, server_default="planning"),
        sa.Column("seafile_url", sa.String(length=500), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["department_id"], ["sys_department.id"], name="fk_pm_project_department"),
        sa.ForeignKeyConstraint(["project_manager_id"], ["sys_user.id"], name="fk_pm_project_manager"),
        sa.UniqueConstraint("code", name="uq_pm_project_code"),
        sa.CheckConstraint(
            "lifecycle_status IN ('planning', 'active', 'completed', 'paused', 'archived')",
            name="ck_pm_project_lifecycle_status",
        ),
        sa.CheckConstraint(
            "planned_end_date >= planned_start_date",
            name="ck_pm_project_date_range",
        ),
    )
    op.create_index("ix_pm_project_code", "pm_project", ["code"], unique=False)

    op.create_table(
        "pm_project_member",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("responsibility", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["project_id"], ["pm_project.id"], name="fk_pm_project_member_project", ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["sys_user.id"], name="fk_pm_project_member_user"),
        sa.UniqueConstraint("project_id", "user_id", name="uq_pm_project_member"),
    )


def downgrade() -> None:
    op.drop_table("pm_project_member")
    op.drop_index("ix_pm_project_code", table_name="pm_project")
    op.drop_table("pm_project")

