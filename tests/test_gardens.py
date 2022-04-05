import tests.util as util

def test_create_garden(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    response = client.post("/gardens", 
                            headers=util.authentication_headers(token),
                            json={"name": "new garden"})
                            
    assert response.status_code == 201
    assert response.json()['name'] == "new garden"
    print(response.json())
    assert response.json().get('id') is not None


def test_get_gardens(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    response = client.post("/gardens", 
                            headers=util.authentication_headers(token),
                            json={"name": "new garden 1"})
                            
    assert response.status_code == 201

    response = client.post("/gardens", 
                            headers=util.authentication_headers(token),
                            json={"name": "new garden 2"})
                            
    assert response.status_code == 201

    response = client.get("/gardens", 
                            headers=util.authentication_headers(token))
                            
    assert response.status_code == 200
    assert len(response.json().get('items')) == 2


def test_get_garden_authorizes(client, basic_user, alt_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)
    alt_token = util.login(client, email=alt_user.email, password=util.ALT_USER_PASSWORD)

    response = client.post("/gardens", 
                            headers=util.authentication_headers(token),
                            json={"name": "new garden"})
                            
    assert response.status_code == 201
    
    garden_id =  response.json().get('id')

    response = client.get(f"/gardens/{garden_id}",
                            headers=util.authentication_headers(alt_token))
    
    assert response.status_code == 404


def test_get_garden(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    response = client.post("/gardens", 
                            headers=util.authentication_headers(token),
                            json={"name": "new garden"})
                            
    assert response.status_code == 201
    
    garden_id =  response.json().get('id')

    response = client.get(f"/gardens/{garden_id}",
                            headers=util.authentication_headers(token))
    
    assert response.status_code == 200
    assert response.json().get('id') == garden_id

def test_patch_garden(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    response = client.post("/gardens", 
                            headers=util.authentication_headers(token),
                            json={"name": "new garden"})
                            
    assert response.status_code == 201
    
    garden_id =  response.json().get('id')

    updated_name = "updated garden"

    response = client.patch(f"/gardens/{garden_id}",
                            headers=util.authentication_headers(token),
                            json={"name": updated_name})

    assert response.status_code == 200
    assert response.json().get('name') == updated_name
