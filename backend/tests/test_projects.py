from datetime import date

import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.session import get_db
from app.main import app
from app.models.project import Project, ProjectLifecycleStatus, ProjectMember
from app.models.system import Department, User, UserRole


@pytest.fixture
def client(session):
    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_user(session, department, role, username):
    user = User(
        username=username,
        display_name=username.split("@")[0],
        password_hash=hash_password("correct-password"),
        role=role,
        department_id=department.id,
    )
    session.add(user)
    session.flush()
    return user


def seed_users(session):
    department_a = Department(name="大数据业务部", code="big-data")
    department_b = Department(name="数据产品部", code="data-product")
    session.add_all([department_a, department_b])
    session.flush()
    users = {
        "pmo": create_user(session, department_a, UserRole.PMO, "pmo@example.com"),
        "head_a": create_user(session, department_a, UserRole.DEPARTMENT_HEAD, "head-a@example.com"),
        "pm_a": create_user(session, department_a, UserRole.PROJECT_MANAGER, "pm-a@example.com"),
        "pm_b": create_user(session, department_b, UserRole.PROJECT_MANAGER, "pm-b@example.com"),
        "member": create_user(session, department_a, UserRole.MEMBER, "member@example.com"),
    }
    session.commit()
    return department_a, department_b, users


def login(client, username):
    response = client.post(
        "/api/auth/login",
        data={"username": username, "password": "correct-password"},
    )
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def project_payload(department_id, manager_id, code="PM-001"):
    return {
        "code": code,
        "name": "数据治理项目",
        "department_id": department_id,
        "project_manager_id": manager_id,
        "client_name": "示例客户",
        "region": "华东",
        "planned_start_date": "2026-01-01",
        "planned_end_date": "2026-12-31",
        "description": "项目基线描述",
        "seafile_url": "https://seafile.example.com/datasets/pm-001",
    }


def test_only_pmo_can_create_project(client, session):
    department, _, users = seed_users(session)

    response = client.post(
        "/api/projects",
        json=project_payload(department.id, users["pm_a"].id),
        headers=login(client, "pmo@example.com"),
    )

    assert response.status_code == 201
    assert response.json()["code"] == "PM-001"
    assert response.json()["lifecycle_status"] == "planning"

    forbidden = client.post(
        "/api/projects",
        json=project_payload(department.id, users["pm_a"].id, code="PM-002"),
        headers=login(client, "pm-a@example.com"),
    )
    assert forbidden.status_code == 403


def test_project_list_respects_role_data_scope(client, session):
    department_a, department_b, users = seed_users(session)
    project_a = Project(
        **project_payload(department_a.id, users["pm_a"].id),
        lifecycle_status=ProjectLifecycleStatus.ACTIVE,
    )
    project_b = Project(
        **project_payload(department_a.id, users["pm_b"].id, code="PM-002"),
        lifecycle_status=ProjectLifecycleStatus.ACTIVE,
    )
    project_c = Project(
        **project_payload(department_b.id, users["pm_b"].id, code="PM-003"),
        lifecycle_status=ProjectLifecycleStatus.ACTIVE,
    )
    session.add_all([project_a, project_b, project_c])
    session.flush()
    session.add(ProjectMember(project_id=project_a.id, user_id=users["member"].id, responsibility="数据开发"))
    session.commit()

    pmo_projects = client.get("/api/projects", headers=login(client, "pmo@example.com"))
    assert {item["code"] for item in pmo_projects.json()} == {"PM-001", "PM-002", "PM-003"}

    head_projects = client.get("/api/projects", headers=login(client, "head-a@example.com"))
    assert {item["code"] for item in head_projects.json()} == {"PM-001", "PM-002"}

    manager_projects = client.get("/api/projects", headers=login(client, "pm-a@example.com"))
    assert {item["code"] for item in manager_projects.json()} == {"PM-001"}

    member_projects = client.get("/api/projects", headers=login(client, "member@example.com"))
    assert {item["code"] for item in member_projects.json()} == {"PM-001"}


def test_archive_hides_project_by_default(client, session):
    department, _, users = seed_users(session)
    project = Project(**project_payload(department.id, users["pm_a"].id))
    session.add(project)
    session.commit()

    headers = login(client, "pmo@example.com")
    archived = client.post(f"/api/projects/{project.id}/archive", headers=headers)
    assert archived.status_code == 200
    assert archived.json()["lifecycle_status"] == "archived"

    assert client.get("/api/projects", headers=headers).json() == []
    visible_archived = client.get("/api/projects?include_archived=true", headers=headers)
    assert [item["code"] for item in visible_archived.json()] == ["PM-001"]


def test_project_update_rejects_end_date_before_start_date(client, session):
    department, _, users = seed_users(session)
    project = Project(**project_payload(department.id, users["pm_a"].id))
    session.add(project)
    session.commit()

    response = client.patch(
        f"/api/projects/{project.id}",
        json={"planned_start_date": "2026-10-01", "planned_end_date": "2026-09-01"},
        headers=login(client, "pm-a@example.com"),
    )

    assert response.status_code == 422

