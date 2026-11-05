from collections.abc import Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.services.authorization import AuthorizationContext, build_authorization_context
from app.models.system import User, UserRole


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证登录凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise credentials_error
    except (JWTError, ValueError, TypeError) as exc:
        raise credentials_error from exc

    user = db.scalar(select(User).where(User.id == int(user_id)))
    if user is None:
        raise credentials_error
    if payload.get("token_version") != user.token_version:
        raise credentials_error
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="用户已停用")
    return user


def require_roles(*roles: UserRole) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有执行此操作的权限")
        return current_user

    return dependency


def get_authorization_context(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> AuthorizationContext:
    return build_authorization_context(db, current_user)


def require_permission(permission_code: str) -> Callable:
    def dependency(context: AuthorizationContext = Depends(get_authorization_context)) -> AuthorizationContext:
        if not context.has_permission(permission_code):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有执行此操作的权限")
        return context

    return dependency


def require_any_permission(*permission_codes: str) -> Callable:
    def dependency(context: AuthorizationContext = Depends(get_authorization_context)) -> AuthorizationContext:
        if not any(context.has_permission(code) for code in permission_codes):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有执行此操作的权限")
        return context

    return dependency

