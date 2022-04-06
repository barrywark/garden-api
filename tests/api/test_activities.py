import tests.util as util


def test_create_activity(client, basic_user, zone_id):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    (_, species_id) = util.garden_fixture(client=client, token=token)

    response = client.post("/activities", 
                            headers=util.authentication_headers(token),
                            json={
                                "zone_id": zone_id, 
                                "species_id": species_id,
                                "description": "my activity"
                            })
                            
    assert response.status_code == 201
    assert response.json().get('id') is not None
    assert response.json().get('description') == "my activity"


def test_get_activities(client, basic_user, zone_id):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    species_id = util.make_species(client=client, token=token).get('id')

    response = client.post("/activities", 
                            headers=util.authentication_headers(token),
                            json={
                                "zone_id": zone_id, 
                                "species_id": species_id,
                                "description": "my activity 1"
                            })

    assert response.status_code == 201


    response = client.post("/activities", 
                            headers=util.authentication_headers(token),
                            json={
                                "zone_id": zone_id, 
                                "species_id": species_id,
                                "description": "my activity 2"
                            })
    assert response.status_code == 201
    
    response = client.get(
        "/activities",
        headers=util.authentication_headers(token)
    )

    assert response.status_code == 200
    assert len(response.json().get('items')) == 2

def test_get_activity_authorizes(client, basic_user, alt_user, zone_id):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)
    alt_token = util.login(client, email=alt_user.email, password=util.ALT_USER_PASSWORD)

    species_id = util.make_species(client=client, token=token).get('id')
    response = client.post("/activities", 
                            headers=util.authentication_headers(token),
                            json={
                                "zone_id": zone_id, 
                                "species_id": species_id,
                                "description": "my activity"
                            })
                            
    assert response.status_code == 201
    
    activity_id =  response.json().get('id')

    response = client.get(f"/activities/{activity_id}",
                            headers=util.authentication_headers(alt_token))
    
    assert response.status_code == 404


def test_get_activity(client, basic_user, alt_user, zone_id):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    species_id = util.make_species(client=client, token=token).get('id')
    response = client.post("/activities", 
                            headers=util.authentication_headers(token),
                            json={
                                "zone_id": zone_id, 
                                "species_id": species_id, 
                                "description": "my activity"})
                            
    assert response.status_code == 201
    
    activity_id =  response.json().get('id')

    response = client.get(f"/activities/{activity_id}",
                            headers=util.authentication_headers(token))
    
    assert response.status_code == 200
    assert response.json().get('id') == activity_id

def test_patch_activity(client, basic_user, zone_id):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    species_id = util.make_species(client=client, token=token).get('id')
    response = client.post("/activities", 
                            headers=util.authentication_headers(token),
                            json={"zone_id": zone_id, "species_id": species_id, "description": "my activity"})
                            
    assert response.status_code == 201
    
    activity_id =  response.json().get('id')

    upated_description = "new description"
    response = client.patch(f"/activities/{activity_id}",
                            headers=util.authentication_headers(token),
                            json={"description": upated_description})

    assert response.status_code == 200
    assert response.json().get('description') == upated_description
