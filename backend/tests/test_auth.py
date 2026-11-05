import pytest
from fastapi.testclient import TestClient

from app.core.security import hash_password
from app.db.session import get_db
from app.main import app
from app.models.system import Department, User, UserRole


@pytest.fixture
def client(session):
    def override_db():
        yield session

    app.dependency_overrides[get_db] = override_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


def create_user(session, *, username="pmo@example.com", is_active=True):
    department = Department(name="大数据业务部", code="big-data")
    session.add(department)
    session.flush()
    session.add(
        User(
            username=username,
            display_name="PMO",
            password_hash=hash_password("correct-password"),
            role=UserRole.PMO,
            department_id=department.id,
            is_active=is_active,
        )
    )
    session.commit()


def test_login_returns_access_token_and_user(client, session):
    create_user(session)

    response = client.post(
        "/api/auth/login",
        data={"username": "pmo@example.com", "password": "correct-password"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["token_type"] == "bearer"
    assert payload["access_token"]
    assert payload["user"]["role"] == "pmo"


def test_invalid_password_returns_401(client, session):
    create_user(session)

    response = client.post(
        "/api/auth/login",
        data={"username": "pmo@example.com", "password": "wrong-password"},
    )

    assert response.status_code == 401


def test_inactive_user_returns_403(client, session):
    create_user(session, is_active=False)

    response = client.post(
        "/api/auth/login",
        data={"username": "pmo@example.com", "password": "correct-password"},
    )

    assert response.status_code == 403


def test_me_returns_current_user(client, session):
    create_user(session)
    login = client.post(
        "/api/auth/login",
        data={"username": "pmo@example.com", "password": "correct-password"},
    )

    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {login.json()['access_token']}"},
    )

    assert response.status_code == 200
    assert response.json()["username"] == "pmo@example.com"


def test_missing_or_malformed_token_returns_401(client):
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers={"Authorization": "Bearer invalid"}).status_code == 401

