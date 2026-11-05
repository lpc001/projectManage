from pydantic import BaseModel, ConfigDict

class RoleSummary(BaseModel):
    code: str
    name: str


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    display_name: str
    department_id: int


class CurrentUserResponse(UserSummary):
    roles: list[RoleSummary]
    menu_permission_codes: list[str]
    action_permission_codes: list[str]
    api_permission_codes: list[str]


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: CurrentUserResponse

