import pytest

import app.models as models
import app.db as db
import app.api.plants as plants

from tests.util import client

from unittest.mock import sentinel

# @pytest.fixture
# def user(session: db.Session) -> models.User:
#     user = models.User(username='fixture')
#     session.add(user)
#     return user


def test_create_species(client):
    response = client.post("/species", json={"name": "new species"})
    print(response.json())
    assert response.status_code == 201
    assert response.json()['name'] == "new species"
    assert response.json().get('id') is not None