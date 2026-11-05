from pydantic import BaseModel, ConfigDict

from app.models.system import UserRole


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    role: UserRole
    department_id: int


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserSummary

