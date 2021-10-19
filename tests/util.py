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

AUTH_EMAIL="authenticated@test.com"


def _authenticated_current_user(the_user: models.User):
    def _current_user(request: fastapi.Request) -> models.User:
    
        request.state.user = the_user

        return request.state.user

    return _current_user


def _unauthenticated_current_user() -> models.User:
    raise fastapi.HTTPException(403)



def _make_user() -> models.User:
    with sql.Session(_ENGINE) as session:
        return auth._get_or_create_user_by_email(session, AUTH_EMAIL)
    

@pytest.fixture
def client() -> TestClient:
    try:
        models.create_all(_ENGINE)
        
        app.dependency_overrides[auth.current_user] = _authenticated_current_user(_make_user())
        app.dependency_overrides[db.get_engine] = lambda: _ENGINE

        yield TestClient(app)
    finally:
        models.drop_all(_ENGINE)


@pytest.fixture
def unauthenticated_client() -> TestClient:
    try:
        #models.create_all(_ENGINE)
        app.dependency_overrides[db.get_engine] = lambda: _ENGINE
        app.dependency_overrides[auth.current_user] = _unauthenticated_current_user

        yield TestClient(app)
    finally:
        # models.drop_all(_ENGINE)
        pass