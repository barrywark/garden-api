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
    assert len(response.json()) == 1
    assert response.json()[0]['name'] == "new species"
    assert response.json()[0].get('id') is not None

def test_get_species_returns_only_authorized_species(client, basic_user, alt_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)
    alt_token = util.login(client, email=alt_user.email, password=util.ALT_USER_PASSWORD)

    create_response = client.post("/species", 
                            headers=util.authentication_headers(token),
                            json={"name": "new species"})
    assert create_response.status_code == 201

    create_response = client.post("/species", 
                            headers=util.authentication_headers(alt_token),
                            json={"name": "alt species"})
    assert create_response.status_code == 201

    response = client.get("/species",
                        headers=util.authentication_headers(token))
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]['name'] == "new species"
    assert response.json()[0].get('id') is not None


def test_get_species_with_no_user(client):
    response = client.get("/species")
    assert response.status_code == 401


def test_get_species_by_id_as_owner(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    create_response = client.post("/species", 
                        headers=util.authentication_headers(token),
                        json={"name": "new species"})
    assert create_response.status_code == 201

    result_id = create_response.json().get('id')

    response = client.get(f"/species/{result_id}",
                            headers=util.authentication_headers(token))
                            
    assert response.status_code == 200
    assert response.json().get('id') == result_id


def test_get_species_by_id_returns_404(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    non_existant_id = 1000
    response = client.get(f"/species/{non_existant_id}",
                            headers=util.authentication_headers(token))
                            
    assert response.status_code == 404


def test_can_patch_species(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    create_response = client.post("/species", 
                        headers=util.authentication_headers(token),
                        json={"name": "new species"})
    assert create_response.status_code == 201

    species_id = create_response.json().get('id')

    updated_name = "updated species"
    patch_response = client.patch(f"/species/{species_id}",
                            headers=util.authentication_headers(token),
                            json={"name": updated_name})

    assert patch_response.status_code == 200

    response = client.get(f"/species/{species_id}",
                            headers=util.authentication_headers(token))

    assert response.status_code == 200
    assert response.json()["name"] == updated_name

def test_cannot_patch_unauthorized_species(client, basic_user, alt_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)
    alt_token = util.login(client, email=alt_user.email, password=util.ALT_USER_PASSWORD)

    create_response = client.post("/species", 
                        headers=util.authentication_headers(token),
                        json={"name": "new species"})
    assert create_response.status_code == 201

    species_id = create_response.json().get('id')

    updated_name = "updated species"
    patch_response = client.patch(f"/species/{species_id}",
                            headers=util.authentication_headers(alt_token),
                            json={"name": updated_name})

    assert patch_response.status_code == 404

    response = client.get(f"/species/{species_id}",
                            headers=util.authentication_headers(token))

    assert response.status_code == 200
    assert response.json()["name"] == "new species"

