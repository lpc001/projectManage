from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.db.session import get_db
from app.models.project import Project
from app.models.system import User
from app.schemas.project import ProjectCreate, ProjectDetail, ProjectListItem, ProjectUpdate
from app.services.projects import archive_project, create_project, get_project, list_projects, update_project


router = APIRouter(prefix="/projects", tags=["项目"])


def to_project_list_item(project: Project) -> ProjectListItem:
    return ProjectListItem(
        id=project.id,
        code=project.code,
        name=project.name,
        department_id=project.department_id,
        project_manager_id=project.project_manager_id,
        project_manager_name=project.project_manager.display_name,
        lifecycle_status=project.lifecycle_status,
        planned_end_date=project.planned_end_date,
        is_archived=project.is_archived,
        updated_at=project.updated_at,
    )


def to_project_detail(project: Project) -> ProjectDetail:
    return ProjectDetail(
        **to_project_list_item(project).model_dump(),
        description=project.description,
        client_name=project.client_name,
        region=project.region,
        planned_start_date=project.planned_start_date,
        seafile_url=project.seafile_url,
    )


@router.get("", response_model=list[ProjectListItem])
def get_projects(
    include_archived: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    authorization=Depends(require_permission("project:list")),
    db: Session = Depends(get_db),
):
    return [to_project_list_item(project) for project in list_projects(db, current_user, include_archived, authorization)]


@router.post("", response_model=ProjectDetail, status_code=status.HTTP_201_CREATED)
def post_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    _authorization=Depends(require_permission("project:create")),
    db: Session = Depends(get_db),
):
    return to_project_detail(create_project(db, payload))


@router.get("/{project_id}", response_model=ProjectDetail)
def get_project_detail(
    project_id: int,
    include_archived: bool = Query(default=False),
    current_user: User = Depends(get_current_user),
    authorization=Depends(require_permission("project:list")),
    db: Session = Depends(get_db),
):
    return to_project_detail(get_project(db, current_user, project_id, include_archived, authorization))


@router.patch("/{project_id}", response_model=ProjectDetail)
def patch_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    authorization=Depends(require_permission("project:update")),
    db: Session = Depends(get_db),
):
    project = get_project(db, current_user, project_id, context=authorization)
    return to_project_detail(update_project(db, current_user, project, payload, authorization))


@router.post("/{project_id}/archive", response_model=ProjectDetail)
def post_archive_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    authorization=Depends(require_permission("project:archive")),
    db: Session = Depends(get_db),
):
    project = get_project(db, current_user, project_id, context=authorization)
    return to_project_detail(archive_project(db, project))

