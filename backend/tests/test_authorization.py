from app.models.authorization import (
    DataScopeType,
    Permission,
    PermissionType,
    Role,
    RoleDepartmentLink,
    RolePermissionLink,
    UserRoleLink,
)
from app.models.system import Department, User
from app.services.authorization import build_authorization_context


def test_multiple_roles_union_permissions_and_scopes(session):
    department_a = Department(name="大数据业务部", code="big-data")
    department_b = Department(name="数据产品部", code="data-product")
    session.add_all([department_a, department_b])
    session.flush()
    user = User(
        username="multi-role@example.com",
        display_name="多角色用户",
        password_hash="hash",
        department_id=department_a.id,
    )
    role_a = Role(code="pmo", name="PMO", data_scope=DataScopeType.DEPARTMENT)
    role_b = Role(code="special-reviewer", name="专项查看员", data_scope=DataScopeType.CUSTOM_DEPARTMENT)
    permission_a = Permission(code="project:list", name="查看项目", permission_type=PermissionType.API)
    permission_b = Permission(code="project:create", name="创建项目", permission_type=PermissionType.API)
    session.add_all([user, role_a, role_b, permission_a, permission_b])
    session.flush()
    session.add_all(
        [
            UserRoleLink(user_id=user.id, role_id=role_a.id),
            UserRoleLink(user_id=user.id, role_id=role_b.id),
            RolePermissionLink(role_id=role_a.id, permission_id=permission_a.id),
            RolePermissionLink(role_id=role_b.id, permission_id=permission_b.id),
            RoleDepartmentLink(role_id=role_b.id, department_id=department_b.id),
        ]
    )
    session.commit()

    context = build_authorization_context(session, user)

    assert context.role_codes == {"pmo", "special-reviewer"}
    assert context.api_permission_codes == {"project:list", "project:create"}
    assert context.data_scope_types == {DataScopeType.DEPARTMENT, DataScopeType.CUSTOM_DEPARTMENT}
    assert context.custom_department_ids == {department_b.id}


def test_all_scope_dominates_other_scopes(session):
    department = Department(name="大数据业务部", code="big-data")
    session.add(department)
    session.flush()
    user = User(
        username="all-scope@example.com",
        display_name="全量用户",
        password_hash="hash",
        department_id=department.id,
    )
    role = Role(code="platform-admin", name="平台管理员", data_scope=DataScopeType.ALL)
    session.add_all([user, role])
    session.flush()
    session.add(UserRoleLink(user_id=user.id, role_id=role.id))
    session.commit()

    context = build_authorization_context(session, user)

    assert context.has_all_data_scope is True

