import pytest

import tests.util as util

import app.models as models

def test_create_zone_with_super_user(client, super_user):
    token = util.login(client, email=super_user.email, password=util.SUPER_USER_PASSWORD)

    response = client.post("/zones", 
                            headers=util.authentication_headers(token),
                            json={"name": "new zone"})
                            
    assert response.status_code == 201
    assert response.json()['name'] == "new zone"
    print(response.json())
    assert response.json().get('id') is not None

def test_create_zone_requires_super_user(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    response = client.post("/zones", 
                            headers=util.authentication_headers(token),
                            json={"name": "new zone"})
                            
    assert response.status_code == 403

def test_get_zones(client, basic_user, super_user):
    super_token = util.login(client, email=super_user.email, password=util.SUPER_USER_PASSWORD)

    crate_response = client.post("/zones", 
                            headers=util.authentication_headers(super_token),
                            json={"name": "new zone"})
                            
    assert crate_response.status_code == 201

    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    response = client.get("/zones",
                        headers=util.authentication_headers(token))
    
    assert response.status_code == 200
    assert len(response.json()) > 0


def test_patch_zone(client, super_user):
    token = util.login(client, email=super_user.email, password=util.SUPER_USER_PASSWORD)

    create_response = client.post("/zones", 
                            headers=util.authentication_headers(token),
                            json={"name": "new zone"})
                            
    assert create_response.status_code == 201
    zone_id = create_response.json()['id']

    updated_name = "updated zone"
    patch_response = client.patch(f"/zones/{zone_id}",
                                    headers=util.authentication_headers(token),
                                    json={"name": updated_name})

    assert patch_response.status_code == 200
    assert patch_response.json()['name'] == updated_name
