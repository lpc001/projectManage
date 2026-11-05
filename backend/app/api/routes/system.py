from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.system import Department, User, UserRole
from app.schemas.system import DepartmentOption, UserOption


router = APIRouter(prefix="/system", tags=["系统选项"])


@router.get("/departments", response_model=list[DepartmentOption])
def get_departments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    query = select(Department).where(Department.is_active.is_(True)).order_by(Department.name)
    if current_user.role in {UserRole.DEPARTMENT_HEAD, UserRole.PROJECT_MANAGER}:
        query = query.where(Department.id == current_user.department_id)
    elif current_user.role not in {UserRole.BOSS, UserRole.PMO, UserRole.PROJECT_MANAGER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有查看部门选项的权限")
    return db.scalars(query).all()


@router.get("/users", response_model=list[UserOption])
def get_users(
    role: UserRole | None = Query(default=None),
    department_id: int | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role not in {UserRole.BOSS, UserRole.PMO, UserRole.DEPARTMENT_HEAD, UserRole.PROJECT_MANAGER}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有查看用户选项的权限")
    query = select(User).where(User.is_active.is_(True))
    if current_user.role in {UserRole.DEPARTMENT_HEAD, UserRole.PROJECT_MANAGER}:
        query = query.where(User.department_id == current_user.department_id)
    elif department_id is not None:
        query = query.where(User.department_id == department_id)
    if role is not None:
        query = query.where(User.role == role)
    return db.scalars(query.order_by(User.display_name)).all()

