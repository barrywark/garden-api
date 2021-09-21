import os

import pytest

from starlette.testclient import TestClient

import sqlmodel as sql
import app.db as db
import app.models as models

from app.main import app

_SQLALCHEMY_DATABASE_URL = "sqlite+pysqlite:///:memory:"

_ENGINE = sql.create_engine(_SQLALCHEMY_DATABASE_URL)

@pytest.fixture
def session(engine=db.ENGINE) -> sql.Session:
    try:
        models.create_all(engine)
        yield db.get_session(engine=engine)
    finally:
        models.drop_all(engine)
    

@pytest.fixture
def client() -> TestClient:
    def _get_db_override():
        return session(engine=_ENGINE)

    app.dependency_overrides[db.get_session] = _get_db_override

    return TestClient(app)

