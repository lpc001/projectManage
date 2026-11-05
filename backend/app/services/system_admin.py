from sqlalchemy import func, select
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import hash_password
from app.models.authorization import (
    AuditLog,
    DataScopeType,
    Permission,
    Role,
    RoleDepartmentLink,
    RolePermissionLink,
    UserRoleLink,
)
from app.models.system import Department, User
from app.schemas.authorization import RoleCreate, RoleDataScopeUpdate, RolePermissionUpdate, RoleUpdate
from app.schemas.system_admin import AdminUserCreate, AdminUserUpdate, DepartmentCreate, DepartmentUpdate


def write_audit(
    db: Session,
    actor: User,
    *,
    action: str,
    target_type: str,
    target_id: int | str | None,
    summary: str,
    result: str = "success",
) -> None:
    db.add(
        AuditLog(
            user_id=actor.id,
            module="system",
            action=action,
            target_type=target_type,
            target_id=str(target_id) if target_id is not None else None,
            result=result,
            summary=summary,
        )
    )


def get_user_roles(db: Session, user_id: int) -> list[Role]:
    return list(
        db.scalars(
            select(Role)
            .join(UserRoleLink, UserRoleLink.role_id == Role.id)
            .where(UserRoleLink.user_id == user_id, Role.is_active.is_(True))
            .order_by(Role.name)
        ).unique().all()
    )


def create_user(db: Session, actor: User, payload: AdminUserCreate) -> User:
    if db.scalar(select(User).where(User.username == payload.username)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="用户名已存在")
    if db.get(Department, payload.department_id) is None:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="部门不存在")
    roles = list(db.scalars(select(Role).where(Role.id.in_(payload.role_ids), Role.is_active.is_(True))).all()) if payload.role_ids else []
    if len(roles) != len(set(payload.role_ids)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="角色不存在或已停用")
    user = User(
        username=payload.username,
        display_name=payload.display_name,
        password_hash=hash_password(payload.password),
        department_id=payload.department_id,
    )
    db.add(user)
    db.flush()
    db.add_all([UserRoleLink(user_id=user.id, role_id=role.id) for role in roles])
    write_audit(db, actor, action="user.create", target_type="user", target_id=user.id, summary=f"创建用户 {user.username}")
    db.commit()
    db.refresh(user)
    return user


def update_user(db: Session, actor: User, user: User, payload: AdminUserUpdate) -> User:
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    write_audit(db, actor, action="user.update", target_type="user", target_id=user.id, summary=f"更新用户 {user.username}")
    db.commit()
    db.refresh(user)
    return user


def set_user_roles(db: Session, actor: User, user: User, role_ids: list[int]) -> User:
    roles = list(db.scalars(select(Role).where(Role.id.in_(role_ids), Role.is_active.is_(True))).all()) if role_ids else []
    if len(roles) != len(set(role_ids)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="角色不存在或已停用")
    user.role_links.clear()
    db.flush()
    db.add_all([UserRoleLink(user_id=user.id, role_id=role.id) for role in roles])
    write_audit(db, actor, action="user.roles.update", target_type="user", target_id=user.id, summary=f"更新用户 {user.username} 的角色")
    db.commit()
    db.refresh(user)
    return user


def disable_user(db: Session, actor: User, user: User) -> User:
    platform_role = db.scalar(select(Role).where(Role.code == "platform_admin"))
    if platform_role:
        active_admin_count = db.scalar(
            select(func.count(User.id))
            .join(UserRoleLink, UserRoleLink.user_id == User.id)
            .where(UserRoleLink.role_id == platform_role.id, User.is_active.is_(True))
        )
        is_platform_admin = any(role.code == "platform_admin" for role in get_user_roles(db, user.id))
        if is_platform_admin and active_admin_count <= 1:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="不能停用最后一个平台管理员")
    user.is_active = False
    user.token_version += 1
    write_audit(db, actor, action="user.disable", target_type="user", target_id=user.id, summary=f"停用用户 {user.username}")
    db.commit()
    db.refresh(user)
    return user


def create_role(db: Session, actor: User, payload: RoleCreate) -> Role:
    if db.scalar(select(Role).where(Role.code == payload.code)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="角色编码已存在")
    role = Role(**payload.model_dump())
    db.add(role)
    db.flush()
    write_audit(db, actor, action="role.create", target_type="role", target_id=role.id, summary=f"创建角色 {role.code}")
    db.commit()
    db.refresh(role)
    return role


def update_role(db: Session, actor: User, role: Role, payload: RoleUpdate) -> Role:
    values = payload.model_dump(exclude_unset=True)
    if role.is_builtin and values.get("is_active") is False and role.code == "platform_admin":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="不能停用平台管理员角色")
    for field, value in values.items():
        setattr(role, field, value)
    write_audit(db, actor, action="role.update", target_type="role", target_id=role.id, summary=f"更新角色 {role.code}")
    db.commit()
    db.refresh(role)
    return role


def set_role_permissions(db: Session, actor: User, role: Role, payload: RolePermissionUpdate) -> Role:
    permissions = list(db.scalars(select(Permission).where(Permission.id.in_(payload.permission_ids), Permission.is_active.is_(True))).all()) if payload.permission_ids else []
    if len(permissions) != len(set(payload.permission_ids)):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="权限不存在或已停用")
    role.permission_links.clear()
    db.flush()
    db.add_all([RolePermissionLink(role_id=role.id, permission_id=permission.id) for permission in permissions])
    write_audit(db, actor, action="role.permissions.update", target_type="role", target_id=role.id, summary=f"更新角色 {role.code} 权限")
    db.commit()
    db.refresh(role)
    return role


def set_role_data_scope(db: Session, actor: User, role: Role, payload: RoleDataScopeUpdate) -> Role:
    if payload.data_scope != DataScopeType.CUSTOM_DEPARTMENT and payload.department_ids:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="只有自定义部门范围需要指定部门")
    if payload.department_ids:
        existing = set(db.scalars(select(Department.id).where(Department.id.in_(payload.department_ids))).all())
        if existing != set(payload.department_ids):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="存在无效部门")
    role.data_scope = payload.data_scope
    role.department_links.clear()
    db.flush()
    db.add_all([RoleDepartmentLink(role_id=role.id, department_id=department_id) for department_id in payload.department_ids])
    write_audit(db, actor, action="role.data_scope.update", target_type="role", target_id=role.id, summary=f"更新角色 {role.code} 数据范围")
    db.commit()
    db.refresh(role)
    return role


def create_department(db: Session, actor: User, payload: DepartmentCreate) -> Department:
    if db.scalar(select(Department).where(Department.code == payload.code)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="部门编码已存在")
    department = Department(**payload.model_dump())
    db.add(department)
    db.flush()
    write_audit(db, actor, action="department.create", target_type="department", target_id=department.id, summary=f"创建部门 {department.code}")
    db.commit()
    db.refresh(department)
    return department


def update_department(db: Session, actor: User, department: Department, payload: DepartmentUpdate) -> Department:
    values = payload.model_dump(exclude_unset=True)
    if values.get("is_active") is False:
        active_users = db.scalar(select(func.count(User.id)).where(User.department_id == department.id, User.is_active.is_(True)))
        if active_users:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="部门仍有启用用户，不能停用")
    for field, value in values.items():
        setattr(department, field, value)
    write_audit(db, actor, action="department.update", target_type="department", target_id=department.id, summary=f"更新部门 {department.code}")
    db.commit()
    db.refresh(department)
    return department

