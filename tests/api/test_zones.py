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