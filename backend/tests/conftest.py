import os

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.db.base import Base
from app.models import system  # noqa: F401


@pytest.fixture(scope="session")
def engine():
    url = os.getenv(
        "TEST_DATABASE_URL",
        "postgresql+psycopg2://postgres:postgres@127.0.0.1:5432/pm_test",
    )
    return create_engine(url, future=True)


@pytest.fixture(autouse=True)
def reset_database(engine):
    Base.metadata.drop_all(engine)
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)
    with engine.begin() as connection:
        connection.execute(text("DROP TABLE IF EXISTS alembic_version"))


@pytest.fixture
def session(engine):
    with Session(engine) as db:
        yield db

