import pytest

# from tests.util import db_tables

@pytest.mark.usefixtures("db_tables")
def test_ping(client):
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"alive": True}
