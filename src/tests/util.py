import os

import pytest

from starlette.testclient import TestClient

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import app.db as db
from app.main import app

# For testing, we use an in-memory database
_ENGINE = create_engine("sqlite+pysqlite:///:memory:", connect_args={"check_same_thread": False})

_SESSION_MAKER = sessionmaker(autocommit=False, autoflush=False, bind=_ENGINE)

@pytest.fixture
def session() -> Session:
    try:
        db.Base.metadata.create_all(_ENGINE)

        session_db = _SESSION_MAKER()
        yield session_db
    finally:
        db.Base.metadata.drop_all(_ENGINE)
    

@pytest.fixture
def client() -> TestClient:
    def _get_db_override():
        return session()

    app.dependency_overrides[db.get_db] = _get_db_override

    return TestClient(app)

