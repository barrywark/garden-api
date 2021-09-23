import os

import pytest

from starlette.testclient import TestClient

import sqlmodel as sql
import app.db as db
import app.models as models
from app.main import app

_SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

_ENGINE = sql.create_engine(_SQLALCHEMY_DATABASE_URL, echo=True, connect_args={"check_same_thread": False})


def _test_db_session() -> sql.Session:
    try:
        print("CREATING TABLES")
        models.create_all(_ENGINE)
        with sql.Session(_ENGINE) as session:
            yield session
    finally:
        models.drop_all(_ENGINE)
    

@pytest.fixture
def client() -> TestClient:

    app.dependency_overrides[db.get_session] = _test_db_session

    return TestClient(app)

