from sqlalchemy.orm import Session

from passbot.db import SessionScoped
from passbot.models import Base

from tests.utils.db import test_engine


class BaseTestCase:

    db_session: Session

    def setup_method(self):
        Base.metadata.create_all(bind=test_engine)
        self.db_session = SessionScoped()

    def teardown_method(self):
        SessionScoped.remove()
        Base.metadata.drop_all(bind=test_engine)
