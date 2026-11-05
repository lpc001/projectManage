from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.project import Project, ProjectLifecycleStatus, ProjectMember
from app.models.system import User, UserRole
from app.schemas.project import ProjectCreate, ProjectUpdate


MANAGEMENT_ROLES = {UserRole.BOSS, UserRole.PMO, UserRole.DEPARTMENT_HEAD}


def _visible_query(user: User) -> Select[tuple[Project]]:
    query = select(Project)
    if user.role in {UserRole.BOSS, UserRole.PMO}:
        return query
    if user.role == UserRole.DEPARTMENT_HEAD:
        return query.where(Project.department_id == user.department_id)
    if user.role == UserRole.PROJECT_MANAGER:
        return query.where(Project.project_manager_id == user.id)
    return query.join(ProjectMember).where(ProjectMember.user_id == user.id)


def list_projects(db: Session, user: User, include_archived: bool = False) -> Sequence[Project]:
    query = _visible_query(user)
    if not include_archived or user.role != UserRole.PMO:
        query = query.where(Project.is_archived.is_(False))
    return db.scalars(query.order_by(Project.updated_at.desc(), Project.id.desc())).unique().all()


def get_project(db: Session, user: User, project_id: int, include_archived: bool = False) -> Project:
    project = db.scalar(select(Project).where(Project.id == project_id))
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    if project.is_archived and not (include_archived and user.role == UserRole.PMO):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    visible = db.scalar(_visible_query(user).where(Project.id == project_id).limit(1))
    if visible is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return project


def create_project(db: Session, payload: ProjectCreate) -> Project:
    manager = db.get(User, payload.project_manager_id)
    if manager is None or not manager.is_active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="项目经理不存在或已停用")
    if manager.department_id != payload.department_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="项目经理必须属于项目所属部门")
    if db.scalar(select(Project).where(Project.code == payload.code)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="项目编码已存在")

    project = Project(
        **payload.model_dump(exclude={"seafile_url"}),
        seafile_url=str(payload.seafile_url) if payload.seafile_url else None,
        lifecycle_status=ProjectLifecycleStatus.PLANNING,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def _assert_can_edit(user: User, project: Project) -> None:
    if user.role in MANAGEMENT_ROLES:
        if user.role == UserRole.DEPARTMENT_HEAD and user.department_id != project.department_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="不能编辑其他部门项目")
        return
    if user.role == UserRole.PROJECT_MANAGER and user.id == project.project_manager_id:
        return
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有编辑此项目的权限")


def update_project(db: Session, user: User, project: Project, payload: ProjectUpdate) -> Project:
    _assert_can_edit(user, project)
    values = payload.model_dump(exclude_unset=True)
    if "seafile_url" in values:
        values["seafile_url"] = str(values["seafile_url"]) if values["seafile_url"] else None

    start_date = values.get("planned_start_date", project.planned_start_date)
    end_date = values.get("planned_end_date", project.planned_end_date)
    if end_date < start_date:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="计划结束日期不能早于计划开始日期")

    department_id = values.get("department_id", project.department_id)
    manager_id = values.get("project_manager_id", project.project_manager_id)
    manager = db.get(User, manager_id)
    if manager is None or not manager.is_active or manager.department_id != department_id:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="项目经理必须属于项目所属部门且处于启用状态")

    for field, value in values.items():
        setattr(project, field, value)
    db.commit()
    db.refresh(project)
    return project


def archive_project(db: Session, project: Project) -> Project:
    project.is_archived = True
    project.lifecycle_status = ProjectLifecycleStatus.ARCHIVED
    db.commit()
    db.refresh(project)
    return project

