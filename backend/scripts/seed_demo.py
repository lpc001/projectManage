from passlib.context import CryptContext

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.authorization import Role, UserRoleLink
from app.models.system import Department, User


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DEPARTMENT_CODE = "big-data"
DEMO_PASSWORD = "ChangeMe123!"
BUSINESS_ROLE_CODES = ["boss", "department_head", "pmo", "project_manager", "member"]


def seed_demo() -> None:
    settings = get_settings()
    if settings.app_env.lower() == "production":
        raise RuntimeError("seed_demo.py cannot run when APP_ENV=production")

    with SessionLocal() as db:
        department = db.query(Department).filter_by(code=DEPARTMENT_CODE).one_or_none()
        if department is None:
            department = Department(name="大数据业务部", code=DEPARTMENT_CODE)
            db.add(department)
            db.flush()

        for role_code in BUSINESS_ROLE_CODES:
            username = f"{role_code}@example.com"
            user = db.query(User).filter_by(username=username).one_or_none()
            if user is None:
                db.add(
                    User(
                        username=username,
                        display_name=role_code,
                        password_hash=pwd_context.hash(DEMO_PASSWORD),
                        department_id=department.id,
                    )
                )
        db.flush()

        roles = {role.code: role for role in db.query(Role).filter(Role.is_active.is_(True)).all()}
        for role_code in BUSINESS_ROLE_CODES:
            username = f"{role_code}@example.com"
            user = db.query(User).filter_by(username=username).one()
            target_role = roles.get(role_code)
            if target_role and db.query(UserRoleLink).filter_by(user_id=user.id, role_id=target_role.id).one_or_none() is None:
                db.add(UserRoleLink(user_id=user.id, role_id=target_role.id))

        admin = db.query(User).filter_by(username="admin@example.com").one_or_none()
        if admin is None:
            admin = User(
                username="admin@example.com",
                display_name="平台管理员",
                password_hash=pwd_context.hash(DEMO_PASSWORD),
                department_id=department.id,
            )
            db.add(admin)
            db.flush()
        admin_role = roles.get("platform_admin")
        if admin_role and db.query(UserRoleLink).filter_by(user_id=admin.id, role_id=admin_role.id).one_or_none() is None:
            db.add(UserRoleLink(user_id=admin.id, role_id=admin_role.id))
        db.commit()

    print("Demo users are ready. Use the development password documented in README.md.")


if __name__ == "__main__":
    seed_demo()

