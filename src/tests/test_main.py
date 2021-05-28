from starlette.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_ping():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong!"}

def test_ping2():
    response = client.get("/pint")
    assert response.status_code == 100