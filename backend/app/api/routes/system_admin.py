from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_permission
from app.db.session import get_db
from app.models.authorization import AuditLog, Permission, Role
from app.models.system import Department, User
from app.schemas.authorization import PermissionResponse, RoleCreate, RoleDataScopeUpdate, RolePermissionUpdate, RoleResponse, RoleUpdate
from app.schemas.system_admin import AdminUserCreate, AdminUserResponse, AdminUserUpdate, AuditResponse, DepartmentCreate, DepartmentResponse, DepartmentUpdate
from app.services.system_admin import (
    create_department,
    create_role,
    create_user,
    disable_user,
    get_user_roles,
    set_role_data_scope,
    set_role_permissions,
    set_user_roles,
    update_department,
    update_role,
    update_user,
)


router = APIRouter(prefix="/system-admin", tags=["系统管理"])


def user_response(db: Session, user: User) -> AdminUserResponse:
    return AdminUserResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        department_id=user.department_id,
        is_active=user.is_active,
        roles=[{"code": role.code, "name": role.name} for role in get_user_roles(db, user.id)],
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户不存在")
    return user


def get_role_or_404(db: Session, role_id: int) -> Role:
    role = db.get(Role, role_id)
    if role is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="角色不存在")
    return role


def get_department_or_404(db: Session, department_id: int) -> Department:
    department = db.get(Department, department_id)
    if department is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="部门不存在")
    return department


@router.get("/users", response_model=list[AdminUserResponse])
def list_users(
    username: str | None = Query(default=None),
    department_id: int | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    _authorization=Depends(require_permission("system:user:list")),
    db: Session = Depends(get_db),
):
    query = select(User).order_by(User.id.desc())
    if username:
        query = query.where(User.username.ilike(f"%{username}%"))
    if department_id is not None:
        query = query.where(User.department_id == department_id)
    if is_active is not None:
        query = query.where(User.is_active.is_(is_active))
    return [user_response(db, user) for user in db.scalars(query).all()]


@router.post("/users", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def post_user(
    payload: AdminUserCreate,
    actor: User = Depends(get_current_user),
    _authorization=Depends(require_permission("system:user:create")),
    db: Session = Depends(get_db),
):
    return user_response(db, create_user(db, actor, payload))


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
def patch_user(
    user_id: int,
    payload: AdminUserUpdate,
    actor: User = Depends(get_current_user),
    _authorization=Depends(require_permission("system:user:update")),
    db: Session = Depends(get_db),
):
    return user_response(db, update_user(db, actor, get_user_or_404(db, user_id), payload))


@router.post("/users/{user_id}/disable", response_model=AdminUserResponse)
def post_disable_user(
    user_id: int,
    actor: User = Depends(get_current_user),
    _authorization=Depends(require_permission("system:user:disable")),
    db: Session = Depends(get_db),
):
    return user_response(db, disable_user(db, actor, get_user_or_404(db, user_id)))


@router.put("/users/{user_id}/roles", response_model=AdminUserResponse)
def put_user_roles(
    user_id: int,
    role_ids: list[int],
    actor: User = Depends(get_current_user),
    _authorization=Depends(require_permission("system:user:update")),
    db: Session = Depends(get_db),
):
    return user_response(db, set_user_roles(db, actor, get_user_or_404(db, user_id), role_ids))


@router.get("/roles", response_model=list[RoleResponse])
def list_roles(_authorization=Depends(require_permission("system:role:list")), db: Session = Depends(get_db)):
    return db.scalars(select(Role).order_by(Role.name)).all()


@router.post("/roles", response_model=RoleResponse, status_code=status.HTTP_201_CREATED)
def post_role(
    payload: RoleCreate,
    actor: User = Depends(get_current_user),
    _authorization=Depends(require_permission("system:role:create")),
    db: Session = Depends(get_db),
):
    return create_role(db, actor, payload)


@router.patch("/roles/{role_id}", response_model=RoleResponse)
def patch_role(
    role_id: int,
    payload: RoleUpdate,
    actor: User = Depends(get_current_user),
    _authorization=Depends(require_permission("system:role:update")),
    db: Session = Depends(get_db),
):
    return update_role(db, actor, get_role_or_404(db, role_id), payload)


@router.put("/roles/{role_id}/permissions", response_model=RoleResponse)
def put_role_permissions(
    role_id: int,
    payload: RolePermissionUpdate,
    actor: User = Depends(get_current_user),
    _authorization=Depends(require_permission("system:role:update")),
    db: Session = Depends(get_db),
):
    return set_role_permissions(db, actor, get_role_or_404(db, role_id), payload)


@router.put("/roles/{role_id}/data-scope", response_model=RoleResponse)
def put_role_data_scope(
    role_id: int,
    payload: RoleDataScopeUpdate,
    actor: User = Depends(get_current_user),
    _authorization=Depends(require_permission("system:role:update")),
    db: Session = Depends(get_db),
):
    return set_role_data_scope(db, actor, get_role_or_404(db, role_id), payload)


@router.get("/permissions", response_model=list[PermissionResponse])
def list_permissions(_authorization=Depends(require_permission("system:permission:list")), db: Session = Depends(get_db)):
    return db.scalars(select(Permission).order_by(Permission.sort_order, Permission.id)).all()


@router.get("/departments", response_model=list[DepartmentResponse])
def list_departments(_authorization=Depends(require_permission("system:department:list")), db: Session = Depends(get_db)):
    return db.scalars(select(Department).order_by(Department.code)).all()


@router.post("/departments", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
def post_department(
    payload: DepartmentCreate,
    actor: User = Depends(get_current_user),
    _authorization=Depends(require_permission("system:department:update")),
    db: Session = Depends(get_db),
):
    return create_department(db, actor, payload)


@router.patch("/departments/{department_id}", response_model=DepartmentResponse)
def patch_department(
    department_id: int,
    payload: DepartmentUpdate,
    actor: User = Depends(get_current_user),
    _authorization=Depends(require_permission("system:department:update")),
    db: Session = Depends(get_db),
):
    return update_department(db, actor, get_department_or_404(db, department_id), payload)


@router.get("/audit", response_model=list[AuditResponse])
def list_audit(_authorization=Depends(require_permission("system:audit:list")), db: Session = Depends(get_db)):
    return db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc(), AuditLog.id.desc())).all()

