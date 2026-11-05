import pytest
from sqlalchemy.exc import IntegrityError

from app.models.system import Department, User, UserRole


def test_all_business_roles_can_be_persisted(session):
    department = Department(name="大数据业务部", code="big-data")
    session.add(department)
    session.flush()

    users = [
        User(
            username=f"{role.value}@example.com",
            display_name=role.value,
            password_hash="hash",
            role=role,
            department_id=department.id,
        )
        for role in UserRole
    ]
    session.add_all(users)
    session.commit()

    assert session.query(User).count() == 5
    assert {user.role for user in session.query(User).all()} == set(UserRole)


def test_usernames_and_department_codes_are_unique(session):
    department = Department(name="大数据业务部", code="big-data")
    session.add(department)
    session.flush()
    session.add(
        User(
            username="pmo@example.com",
            display_name="PMO",
            password_hash="hash",
            role=UserRole.PMO,
            department_id=department.id,
        )
    )
    session.commit()

    session.add(Department(name="重复部门", code="big-data"))
    with pytest.raises(IntegrityError):
        session.commit()

