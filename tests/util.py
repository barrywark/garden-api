import fastapi
import pytest

from starlette.testclient import TestClient

import sqlmodel as sql
import app.db as db
import app.models as models
import app.auth as auth

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

def _authenticated_current_user() -> models.User:
    with sql.Session(_ENGINE) as session:
        auth_user = models.User(email="authenticated@test.com")
        session.add(auth_user)
        session.commit()
        session.refresh(auth_user)

        return auth_user
    
def _unauthenticated_current_user() -> models.User:
    raise fastapi.HTTPException(403)



@pytest.fixture
def client() -> TestClient:

    app.dependency_overrides[db.get_session] = _test_db_session
    app.dependency_overrides[auth.current_user] = _authenticated_current_user

    return TestClient(app)


@pytest.fixture
def unauthenticated_client() -> TestClient:

    app.dependency_overrides[db.get_session] = _test_db_session
    app.dependency_overrides[auth.current_user] = _unauthenticated_current_user

    return TestClient(app)