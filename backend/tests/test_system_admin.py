import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.session import get_db
from app.main import app
from app.models.authorization import DataScopeType, Permission, PermissionType, Role, RolePermissionLink, UserRoleLink
from app.models.system import Department, User, UserRole


@pytest.fixture
def client(session):
    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def setup_admin(session):
    department = Department(name="大数据业务部", code="big-data")
    session.add(department)
    session.flush()
    admin_role = Role(code="platform_admin", name="平台管理员", data_scope=DataScopeType.ALL, is_builtin=True)
    member_role = Role(code="member", name="项目成员", data_scope=DataScopeType.MEMBER, is_builtin=True)
    permission_codes = [
        "system:user:list",
        "system:user:create",
        "system:user:update",
        "system:user:disable",
        "system:role:list",
        "system:role:create",
        "system:role:update",
        "system:permission:list",
        "system:department:list",
        "system:department:update",
        "system:audit:list",
    ]
    permissions = [
        Permission(code=code, name=code, permission_type=PermissionType.API)
        for code in permission_codes
    ]
    admin = User(
        username="admin@example.com",
        display_name="平台管理员",
        password_hash=hash_password("correct-password"),
        role=UserRole.PMO,
        department_id=department.id,
    )
    member = User(
        username="member@example.com",
        display_name="项目成员",
        password_hash=hash_password("correct-password"),
        role=UserRole.MEMBER,
        department_id=department.id,
    )
    session.add_all([admin_role, member_role, *permissions, admin, member])
    session.flush()
    session.add_all(
        [UserRoleLink(user_id=admin.id, role_id=admin_role.id)]
        + [RolePermissionLink(role_id=admin_role.id, permission_id=permission.id) for permission in permissions]
    )
    session.commit()
    return admin, member, department, admin_role, member_role


def login(client, username):
    response = client.post(
        "/api/auth/login",
        data={"username": username, "password": "correct-password"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_non_admin_cannot_access_system_management(client, session):
    _, member, _, _, _ = setup_admin(session)

    response = client.get("/api/system-admin/users", headers=login(client, member.username))

    assert response.status_code == 403


def test_platform_admin_can_create_user_and_assign_roles(client, session):
    admin, _, department, _, member_role = setup_admin(session)
    headers = login(client, admin.username)

    response = client.post(
        "/api/system-admin/users",
        headers=headers,
        json={
            "username": "new-member@example.com",
            "display_name": "新成员",
            "password": "new-password",
            "department_id": department.id,
            "role_ids": [member_role.id],
        },
    )

    assert response.status_code == 201
    assert response.json()["username"] == "new-member@example.com"
    assert response.json()["roles"][0]["code"] == "member"

    audit = client.get("/api/system-admin/audit", headers=headers)
    assert audit.status_code == 200
    assert any(item["action"] == "user.create" for item in audit.json())


def test_last_platform_admin_cannot_be_disabled(client, session):
    admin, _, _, _, _ = setup_admin(session)
    response = client.post(
        f"/api/system-admin/users/{admin.id}/disable",
        headers=login(client, admin.username),
    )

    assert response.status_code == 409


def test_platform_admin_can_create_role(client, session):
    admin, _, _, _, _ = setup_admin(session)
    response = client.post(
        "/api/system-admin/roles",
        headers=login(client, admin.username),
        json={
            "code": "reviewer",
            "name": "专项评审员",
            "description": "查看专项项目",
            "data_scope": "department",
        },
    )

    assert response.status_code == 201
    assert response.json()["code"] == "reviewer"

