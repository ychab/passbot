from typing import Generator

import pytest
from sqlalchemy import Engine

from passbot import settings
from passbot.db import SessionScoped
from passbot.models import Base

from tests.utils.db import configure_sessionmakers, init_db


@pytest.fixture(scope="session", autouse=True)
def test_engine() -> Generator:
    test_db_name: str = f"test_{settings.POSTGRES_DB}"

    init_db(test_db_name)
    engine: Engine = configure_sessionmakers(test_db_name)
    yield engine


@pytest.fixture
def session_db(test_engine) -> Generator:
    Base.metadata.create_all(bind=test_engine)
    session_db = SessionScoped()

    yield session_db

    SessionScoped.remove()
    Base.metadata.drop_all(bind=test_engine)
