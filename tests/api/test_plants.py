import pytest

import app.models as models
import app.db as db
import app.api.plants as plants

from tests.util import session, client

from unittest.mock import sentinel

@pytest.fixture
def user(session: db.Session) -> models.User:
    user = models.User(username='fixture')
    session.add(user)
    return user


def test_create_species(client, user):
    response = client.post("/species", {"name": "new species",
                                        "owner": user})
    assert response.status_code == 201
    assert response.json() == {}