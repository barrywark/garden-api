import typing
import pytest

from starlette.testclient import TestClient
from app.main import app


@pytest.fixture
def client() -> typing.Iterable[TestClient]:

    yield TestClient(app)
