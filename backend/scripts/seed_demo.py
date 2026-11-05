from passlib.context import CryptContext

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.models.system import Department, User, UserRole


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
DEPARTMENT_CODE = "big-data"
DEMO_PASSWORD = "ChangeMe123!"


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

        for role in UserRole:
            username = f"{role.value}@example.com"
            user = db.query(User).filter_by(username=username).one_or_none()
            if user is None:
                db.add(
                    User(
                        username=username,
                        display_name=role.value,
                        password_hash=pwd_context.hash(DEMO_PASSWORD),
                        role=role,
                        department_id=department.id,
                    )
                )
        db.commit()

    print("Demo users are ready. Use the development password documented in README.md.")


if __name__ == "__main__":
    seed_demo()

