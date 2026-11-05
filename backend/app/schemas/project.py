from datetime import date, datetime

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, model_validator

from app.models.project import ProjectLifecycleStatus


class ProjectCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    department_id: int
    project_manager_id: int
    client_name: str | None = None
    region: str | None = None
    planned_start_date: date
    planned_end_date: date
    seafile_url: AnyHttpUrl | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.planned_end_date < self.planned_start_date:
            raise ValueError("计划结束日期不能早于计划开始日期")
        return self


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    department_id: int | None = None
    project_manager_id: int | None = None
    client_name: str | None = None
    region: str | None = None
    planned_start_date: date | None = None
    planned_end_date: date | None = None
    lifecycle_status: ProjectLifecycleStatus | None = None
    seafile_url: AnyHttpUrl | None = None

    @model_validator(mode="after")
    def validate_dates(self):
        if self.planned_start_date and self.planned_end_date:
            if self.planned_end_date < self.planned_start_date:
                raise ValueError("计划结束日期不能早于计划开始日期")
        return self


class ProjectListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    name: str
    department_id: int
    project_manager_id: int
    project_manager_name: str
    lifecycle_status: ProjectLifecycleStatus
    planned_end_date: date
    is_archived: bool
    updated_at: datetime


class ProjectDetail(ProjectListItem):
    description: str | None
    client_name: str | None
    region: str | None
    planned_start_date: date
    seafile_url: str | None

