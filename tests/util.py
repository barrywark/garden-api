import typing
import contextlib
import pytest

from fastapi_users.manager import UserAlreadyExists
from starlette.testclient import TestClient

import app.settings as settings
import app.db as db
import app.models as models
import app.api.users as users

from app.main import app


def get_settings_override() -> settings.Settings:
    """
    Override test settings
    """

    return settings.Settings(
        testing=True,
        database_url="sqlite+aiosqlite://"
    )

@pytest.fixture
async def client() -> typing.AsyncGenerator[TestClient, None]:
    """
    Create a test client with test-specific settings
    """
    
    engine = db.get_engine(settings=get_settings_override())

    # reset database tables
    await db.drop_tables(engine=engine)
    await db.create_db_and_tables(engine=engine)

    with TestClient(app) as test_client:
        # testing
        yield test_client



def login(test_client: TestClient, email: str, password: str) -> str:
    """
    Return access token for user via /auth/jwt/login
    """

    auth_response = test_client.post('/auth/jwt/login', 
        data={"username": email, "password": password})
    
    assert auth_response.status_code == 200
    token = auth_response.json()['access_token']

    return token

def authentication_headers(token: str) -> dict[str,str]:
    return {'Authorization': f'Bearer {token}'}


get_engine_context = contextlib.asynccontextmanager(db.get_engine)
get_async_session_maker_context = contextlib.asynccontextmanager(db.get_async_session_maker)
get_async_session_context = contextlib.asynccontextmanager(db.get_async_session)
get_user_db_context = contextlib.asynccontextmanager(db.get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(users.get_user_manager)


async def create_user(email: str, password: str, is_superuser: bool = False) -> models.User:
    """
    Create a user via UserManager. For use outside dependency injection
    """

    try:
        engine = db.get_engine(settings=get_settings_override())
        session_maker = db.get_async_session_maker(engine=engine)
        async with get_async_session_context(async_session_maker=session_maker) as session:
            async with get_user_db_context(session) as user_db:
                async with get_user_manager_context(user_db) as user_manager:
                    user = await user_manager.create(
                        models.UserCreateModel(
                            email=email, password=password, is_superuser=is_superuser
                        )
                    )
                    print(f"User created {user}")
                    return user

    except UserAlreadyExists:
        print(f"User {email} already exists")


BASIC_USER_EMAIL = 'user@test.com'
BASIC_USER_PASSWORD = 'NOT SECRET'
@pytest.fixture
async def basic_user()  -> typing.AsyncGenerator[models.User, None]:
    """
    Verified, active, non-superuser User
    """

    yield await create_user(email=BASIC_USER_EMAIL, password=BASIC_USER_PASSWORD, is_superuser=False)

ALT_USER_EMAIL = 'alt@test.com'
ALT_USER_PASSWORD = 'NOT SECRET'
@pytest.fixture
async def alt_user()  -> typing.AsyncGenerator[models.User, None]:
    """
    Alternate verified, active, non-superuser User
    """

    yield await create_user(email=ALT_USER_EMAIL, password=ALT_USER_PASSWORD, is_superuser=False)