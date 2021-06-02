import pytest
import uuid

import app.models as models
import sqlalchemy as sql
import sqlalchemy.orm as orm

from tests.util import client, session

@pytest.fixture
def user(session) -> models.User:
    with session.begin():
        u = models.User(email='test@test.com', fullname='Foo Bar')
        session.add(u)

        return u


def test_user_found_by_guid(user: models.User, session: orm.Session):
    assert user.guid is not None
    
    u2 = session.query(models.User).filter_by(guid=user.guid).first()
    assert u2.guid == user.guid
    assert u2 is user