import tests.util as util

def test_create_planting(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    (garden_id, species_id) = util.garden_fixture(client=client, token=token)
    response = client.post("/plantings", 
                            headers=util.authentication_headers(token),
                            json={"garden_id": garden_id, "species_id": species_id})
                            
    assert response.status_code == 201
    assert response.json().get('id') is not None


def test_get_plantings(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    (garden_id, species_id) = util.garden_fixture(client=client, token=token)
    response = client.post("/plantings", 
                            headers=util.authentication_headers(token),
                            json={"garden_id": garden_id, "species_id": species_id})
                            
    assert response.status_code == 201

    response = client.post("/plantings", 
                            headers=util.authentication_headers(token),
                            json={"garden_id": garden_id, "species_id": species_id})
                            
    assert response.status_code == 201

    response = client.get("/plantings", 
                            headers=util.authentication_headers(token))
                            
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_planting_authorizes(client, basic_user, alt_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)
    alt_token = util.login(client, email=alt_user.email, password=util.ALT_USER_PASSWORD)

    (garden_id, species_id) = util.garden_fixture(client=client, token=token)
    response = client.post("/plantings", 
                            headers=util.authentication_headers(token),
                            json={"garden_id": garden_id, "species_id": species_id})
                            
    assert response.status_code == 201
    
    planting_id =  response.json().get('id')

    response = client.get(f"/plantings/{planting_id}",
                            headers=util.authentication_headers(alt_token))
    
    assert response.status_code == 404


def test_get_planting(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    (garden_id, species_id) = util.garden_fixture(client=client, token=token)
    response = client.post("/plantings", 
                            headers=util.authentication_headers(token),
                            json={"garden_id": garden_id, "species_id": species_id})
                            
    assert response.status_code == 201
                            
    planting_id =  response.json().get('id')

    response = client.get(f"/plantings/{planting_id}",
                            headers=util.authentication_headers(token))
    
    assert response.status_code == 200
    assert response.json().get('id') == planting_id

def test_patch_planting(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    (garden_id, species_id) = util.garden_fixture(client=client, token=token)
    response = client.post("/plantings", 
                            headers=util.authentication_headers(token),
                            json={"garden_id": garden_id, "species_id": species_id})
                            
    assert response.status_code == 201
    
    planting_id =  response.json().get('id')

    updated_species_id = util.make_species(client=client, token=token).get('id')

    response = client.patch(f"/plantings/{planting_id}",
                            headers=util.authentication_headers(token),
                            json={"species_id": updated_species_id})

    assert response.status_code == 200
    assert response.json().get('species_id') == updated_species_id
