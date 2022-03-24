
async def test_ping(client):
    """
    /ping should return HTTP OK
    """
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"alive": True}
