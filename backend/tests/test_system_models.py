import pytest
from sqlalchemy.exc import IntegrityError

from app.models.authorization import DataScopeType, Permission, PermissionType, Role, UserRoleLink
from app.models.system import Department, User


def test_all_business_roles_can_be_persisted(session):
    department = Department(name="大数据业务部", code="big-data")
    session.add(department)
    session.flush()

    roles = [Role(code=code, name=code, data_scope=DataScopeType.MEMBER) for code in ["boss", "department_head", "pmo", "project_manager", "member"]]
    users = [User(username=f"{role.code}@example.com", display_name=role.name, password_hash="hash", department_id=department.id) for role in roles]
    session.add_all(roles + users)
    session.flush()
    session.add_all([UserRoleLink(user_id=user.id, role_id=role.id) for user, role in zip(users, roles, strict=True)])
    session.commit()

    assert session.query(User).count() == 5
    assert session.query(UserRoleLink).count() == 5


def test_usernames_and_department_codes_are_unique(session):
    department = Department(name="大数据业务部", code="big-data")
    session.add(department)
    session.flush()
    session.add(
        User(
            username="pmo@example.com",
            display_name="PMO",
            password_hash="hash",
            department_id=department.id,
        )
    )
    session.commit()

    session.add(Department(name="重复部门", code="big-data"))
    with pytest.raises(IntegrityError):
        session.commit()


def test_role_and_permission_codes_are_unique(session):
    role = Role(code="pmo", name="PMO", data_scope=DataScopeType.ALL)
    permission = Permission(code="project:list", name="查看项目", permission_type=PermissionType.API)
    session.add_all([role, permission])
    session.commit()

    session.add(Role(code="pmo", name="重复角色", data_scope=DataScopeType.MEMBER))
    with pytest.raises(IntegrityError):
        session.commit()

