import typing
import pytest
import fastapi_users
from starlette.testclient import TestClient

import app.settings as settings
import app.db as db
import app.models as models

from app.main import app


def get_settings_override() -> settings.Settings:
    """
    Override test settings
    """

    return settings.Settings(
        testing=1,
        database_url="sqlite+aiosqlite:///memory:"
    )

@pytest.fixture
async def client() -> typing.AsyncGenerator[TestClient, None]:
    """
    Create a test client with test-specific settings
    """
    
    # create database tables
    engine = db.get_engine(settings=get_settings_override())
    await db.create_db_and_tables(engine=engine)

    with TestClient(app) as test_client:
        # testing
        yield test_client

    # tear down
    await db.drop_tables(engine=db.get_engine(settings=get_settings_override()))


# @pytest.fixture
# @pytest.mark.asyncio
# async def basic_user() -> models.UserDB:
#     """
#     Verified, active, non-superuser User
#     """
#     user_create = models.UserCreate(
#         username='test_user',
#         password='test123',
#         email='test@example.com',
#         is_active=True,
#         is_superuser=False,
#         is_verified=True
#     )

#     user = await fastapi_users.create_user(user_create)
    
#     yield user

