from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.system import User
from app.schemas.auth import CurrentUserResponse, LoginResponse
from app.services.auth import authenticate_user, build_current_user_response, build_login_response


router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="用户已停用")
    return build_login_response(db, user)


@router.get("/me", response_model=CurrentUserResponse)
def me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> CurrentUserResponse:
    return build_current_user_response(db, current_user)

