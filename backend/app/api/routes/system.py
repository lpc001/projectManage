from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.db.session import get_db
from app.models.authorization import Role, UserRoleLink
from app.models.system import Department, User
from app.schemas.system import DepartmentOption, UserOption
from app.services.authorization import AuthorizationContext


router = APIRouter(prefix="/system", tags=["系统选项"])


@router.get("/departments", response_model=list[DepartmentOption])
def get_departments(
    current_user: User = Depends(get_current_user),
    authorization: AuthorizationContext = Depends(require_permission("system:department:lookup")),
    db: Session = Depends(get_db),
):
    query = select(Department).where(Department.is_active.is_(True)).order_by(Department.name)
    if not authorization.has_all_data_scope:
        department_ids = {current_user.department_id} | authorization.custom_department_ids
        query = query.where(Department.id.in_(department_ids))
    return db.scalars(query).all()


@router.get("/users", response_model=list[UserOption])
def get_users(
    role: str | None = Query(default=None),
    department_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    authorization: AuthorizationContext = Depends(require_permission("system:user:lookup")),
    db: Session = Depends(get_db),
):
    query = select(User).where(User.is_active.is_(True))
    if not authorization.has_all_data_scope:
        department_ids = {current_user.department_id} | authorization.custom_department_ids
        query = query.where(User.department_id.in_(department_ids))
    elif department_id is not None:
        query = query.where(User.department_id == department_id)
    if role is not None:
        query = query.join(UserRoleLink, UserRoleLink.user_id == User.id).join(Role, Role.id == UserRoleLink.role_id).where(Role.code == role)
    users = db.scalars(query.order_by(User.display_name)).unique().all()
    return [
        UserOption(
            id=user.id,
            username=user.username,
            display_name=user.display_name,
            role=role or (user.roles[0].code if user.roles else ""),
            department_id=user.department_id,
        )
        for user in users
    ]

