from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, verify_password
from app.models.authorization import Role, UserRoleLink
from app.models.system import User
from app.schemas.auth import CurrentUserResponse, RoleSummary
from app.services.authorization import build_authorization_context


def authenticate_user(db: Session, username: str, password: str) -> User | None:
    user = db.scalar(select(User).where(User.username == username))
    if user is None or not verify_password(password, user.password_hash):
        return None
    return user


def build_current_user_response(db: Session, user: User) -> CurrentUserResponse:
    context = build_authorization_context(db, user)
    role_rows = db.execute(
        select(UserRoleLink.role_id, Role.code, Role.name)
        .join(Role, Role.id == UserRoleLink.role_id)
        .where(UserRoleLink.user_id == user.id, Role.is_active.is_(True))
    ).all()
    return CurrentUserResponse(
        id=user.id,
        username=user.username,
        display_name=user.display_name,
        department_id=user.department_id,
        roles=[RoleSummary(code=row.code, name=row.name) for row in role_rows],
        menu_permission_codes=sorted(context.menu_permission_codes),
        action_permission_codes=sorted(context.action_permission_codes),
        api_permission_codes=sorted(context.api_permission_codes),
    )


def build_login_response(db: Session, user: User) -> dict[str, object]:
    return {
        "access_token": create_access_token(user),
        "token_type": "bearer",
        "user": build_current_user_response(db, user),
    }

