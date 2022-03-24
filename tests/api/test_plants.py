import pytest

import tests.util as util

import app.models as models


def test_create_species_with_active_user(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    response = client.post("/species", 
                            headers=util.authentication_headers(token),
                            json={"name": "new species"})
                            
    assert response.status_code == 201
    assert response.json()['name'] == "new species"
    print(response.json())
    assert response.json().get('id') is not None


def test_create_species_no_user(client):
    response = client.post("/species", json={"name": "new species"})
    assert response.status_code == 401


def test_get_species_owned_by_user(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    create_response = client.post("/species", 
                            headers=util.authentication_headers(token),
                            json={"name": "new species"})
    assert create_response.status_code == 201

    response = client.get("/species",
                        headers=util.authentication_headers(token))
    assert response.status_code == 200
    assert response.json()[0]['name'] == "new species"
    assert response.json()[0].get('id') is not None

# def test_get_species_with_no_user(client):
#     # u = make_user(session=fixture_db_session)
#     # owner = fixture_db_session.get(models.User, u.id)
#     # fixture_db_session.add(models.Species(name="test species", owner=owner))
#     # fixture_db_session.commit()

#     response = unauthenticated_client.get("/species")
#     assert response.status_code == 403


# def test_get_species_by_id(client):
#     create_response = client.post("/species", json={"name": "new species"})
#     assert create_response.status_code == 201

#     result_id = create_response.json().get('id')

#     response = client.get(f"/species/{result_id}")
#     assert response.status_code == 200
#     assert response.json().get('id') == result_id