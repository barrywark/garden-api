import pytest

import app.models as models
import app.db as db
import app.api.plants as plants

from tests.util import client, unauthenticated_client

from unittest.mock import sentinel

# @pytest.fixture
# def user(session: db.Session) -> models.User:
#     user = models.User(username='fixture')
#     session.add(user)
#     return user


def test_create_species_with_active_user(client):
    response = client.post("/species", json={"name": "new species"})
    assert response.status_code == 201
    assert response.json()['name'] == "new species"
    assert response.json().get('id') is not None


def test_create_species_no_user(unauthenticated_client):
    response = unauthenticated_client.post("/species", json={"name": "new species"})
    assert response.status_code == 403


def test_get_species_with_active_user(client):
    create_response = client.post("/species", json={"name": "new species"})
    assert create_response.status_code == 201

    response = client.get("/species")
    assert response.status_code == 200
    assert response.json()[0]['name'] == "new species"
    assert response.json()[0].get('id') is not None

def test_get_species_with_no_user(unauthenticated_client, client):
    create_response = client.post("/species", json={"name": "new species"})
    assert create_response.status_code == 201

    response = unauthenticated_client.get("/species")
    assert response.status_code == 200
    assert len(response.json()) == 0


def test_get_species_by_id(client):
    create_response = client.post("/species", json={"name": "new species"})
    assert create_response.status_code == 201

    id = create_response.json().get('id')

    response = client.get("/species/{}".format(id))
    assert response.status_code == 200
    assert response.json().get('id') == id