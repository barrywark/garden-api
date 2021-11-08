import pytest

import app.models as models

from tests.util import make_user


@pytest.mark.usefixtures("db_tables")
def test_create_species_with_active_user(client):
    response = client.post("/species", json={"name": "new species"})
    assert response.status_code == 201
    assert response.json()['name'] == "new species"
    assert response.json().get('id') is not None


@pytest.mark.usefixtures("db_tables")
def test_create_species_no_user(unauthenticated_client):
    response = unauthenticated_client.post("/species", json={"name": "new species"})
    assert response.status_code == 403


@pytest.mark.usefixtures("db_tables")
def test_get_species_with_active_user(client):
    create_response = client.post("/species", json={"name": "new species"})
    assert create_response.status_code == 201

    response = client.get("/species")
    assert response.status_code == 200
    assert response.json()[0]['name'] == "new species"
    assert response.json()[0].get('id') is not None

@pytest.mark.usefixtures("db_tables")
def test_get_species_with_no_user(unauthenticated_client, fixture_db_session):
    u = make_user(session=fixture_db_session)
    owner = fixture_db_session.get(models.User, u.id)
    fixture_db_session.add(models.Species(name="test species", owner=owner))
    fixture_db_session.commit()

    response = unauthenticated_client.get("/species")
    assert response.status_code == 403


@pytest.mark.usefixtures("db_tables")
def test_get_species_by_id(client):
    create_response = client.post("/species", json={"name": "new species"})
    assert create_response.status_code == 201

    id = create_response.json().get('id')

    response = client.get("/species/{}".format(id))
    assert response.status_code == 200
    assert response.json().get('id') == id