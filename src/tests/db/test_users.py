import pytest
import uuid

import app.models as models
import app.api.users as users
import sqlalchemy as sql
import sqlalchemy.orm as orm

from tests.util import client, session

@pytest.fixture
def user(session) -> models.User:
    with session.begin():
        u = models.User(email='test@test.com', fullname='Foo Bar')
        session.add(u)
        return u

def test_guid_unique(user: models.User, session: orm.Session):
    with pytest.raises(sql.exc.IntegrityError):
        session.add(models.User(guid=user.guid))
        session.commit()

def test_email_unique(user: models.User, session: orm.Session):
    with pytest.raises(sql.exc.IntegrityError):
        session.add(models.User(email=user.email))
        session.commit()


def test_get_user_by_guid_finds_user(user: models.User, session: orm.Session):
    assert users.get_user_by_guid(session, user.guid).id == user.id


def test_get_user_by_guid_returns_none_if_no_user(user: models.User, session: orm.Session):
    assert users.get_user_by_guid(session, uuid.uuid4()) is None


def test_get_user_by_id_finds_user(user: models.User, session: orm.Session):
    u2 = users.get_user_by_id(session, user.id)
    assert u2 is user


def test_get_user_by_id_return_none_if_no_user(user: models.User, session: orm.Session):
    assert users.get_user_by_id(session, user.id + 1) is None