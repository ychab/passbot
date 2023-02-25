import os
from typing import cast

import pytest

from _pytest.main import Session

from tests.utils.db import configure_sessionmakers, init_db


@pytest.hookimpl(trylast=True)
def pytest_sessionstart(session: Session):
    db_name: str = cast(str, os.getenv("POSTGRES_DB", ""))
    test_db_name: str = f"test_{db_name}"  # For now, don't support parallel execution (i.e: pytest-xdist)

    init_db(test_db_name)
    configure_sessionmakers(test_db_name)
