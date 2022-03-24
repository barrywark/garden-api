import pytest
import tests.util as util

@pytest.mark.asyncio
async def test_authping_with_authenticated_user(client, basic_user):
    token = util.login(client, email=basic_user.email, password=util.BASIC_USER_PASSWORD)

    response = client.get("/auth-ping",
        headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_authping_without_authenticated_user(client):
    token = ''

    response = client.get("/auth-ping",
        headers={'Authorization': f'Bearer {token}'})
    
    assert response.status_code == 401