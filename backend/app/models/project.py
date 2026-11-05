from datetime import date
from enum import StrEnum

from sqlalchemy import Boolean, Date, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ProjectLifecycleStatus(StrEnum):
    PLANNING = "planning"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ARCHIVED = "archived"


class Project(TimestampMixin, Base):
    __tablename__ = "pm_project"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    department_id: Mapped[int] = mapped_column(ForeignKey("sys_department.id"), nullable=False)
    project_manager_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), nullable=False)
    client_name: Mapped[str | None] = mapped_column(String(200))
    region: Mapped[str | None] = mapped_column(String(100))
    planned_start_date: Mapped[date] = mapped_column(Date, nullable=False)
    planned_end_date: Mapped[date] = mapped_column(Date, nullable=False)
    lifecycle_status: Mapped[ProjectLifecycleStatus] = mapped_column(
        Enum(
            ProjectLifecycleStatus,
            name="project_lifecycle_status",
            native_enum=False,
            create_constraint=True,
            values_callable=lambda status_enum: [status.value for status in status_enum],
        ),
        nullable=False,
        default=ProjectLifecycleStatus.PLANNING,
    )
    seafile_url: Mapped[str | None] = mapped_column(String(500))
    is_archived: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    department = relationship("Department")
    project_manager = relationship("User", foreign_keys=[project_manager_id])
    members: Mapped[list["ProjectMember"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )


class ProjectMember(TimestampMixin, Base):
    __tablename__ = "pm_project_member"
    __table_args__ = (UniqueConstraint("project_id", "user_id", name="uq_pm_project_member"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("pm_project.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("sys_user.id"), nullable=False)
    responsibility: Mapped[str | None] = mapped_column(String(200))

    project: Mapped[Project] = relationship(back_populates="members")
    user = relationship("User")

