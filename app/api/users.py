import uuid
from typing import Optional, Any

import fastapi

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers, UUIDIDMixin
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlmodel import SQLModelUserDatabase

from app.db import get_user_db
import app.models as models
from app.settings import get_settings

SECRET = get_settings().jwt_secret or "NOT SECRET"
JWT_LIFETIME_SECONDS = get_settings().jwt_lifetime_seconds


class UserManager(UUIDIDMixin, BaseUserManager[models.UserCreateModel, models.User]):
    """
    UserManager class
    """
    user_db_model = models.User
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: models.User,
                                request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_forgot_password(
            self, user: models.User, token: str, request: Optional[Request] = None):
        print(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
            self, user: models.User, token: str, request: Optional[Request] = None):
        print(f"Verification requested for user {user.id}. Verification token: {token}")


async def get_user_manager(user_db: SQLModelUserDatabase = Depends(get_user_db)):
    """
    Usage:

    async def myfun(user_manager: UserManager = Depends(get_user_manager)):
        pass
    """
    yield UserManager(user_db)


bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=JWT_LIFETIME_SECONDS)


auth_backend = AuthenticationBackend(name="jwt",
                                     transport=bearer_transport,
                                     get_strategy=get_jwt_strategy)

fastapi_users = FastAPIUsers[models.User, uuid.UUID](
    get_user_manager,
    (auth_backend,),
)


def make_router():
    """
    fastapi-users routes
    """

    router = fastapi.APIRouter()

    router.include_router(
        fastapi_users.get_auth_router(auth_backend),
        prefix="/auth/jwt",
        tags=["auth"])

    router.include_router(
        fastapi_users.get_register_router(models.UserRead, models.UserCreateModel),
        prefix="/auth",
        tags=["auth"])

    router.include_router(
        fastapi_users.get_reset_password_router(),
        prefix="/auth",
        tags=["auth"])

    router.include_router(
        fastapi_users.get_verify_router(models.UserRead),
        prefix="/auth",
        tags=["auth"])

    router.include_router(
        fastapi_users.get_users_router(models.UserRead, models.UserUpdateModel),
        prefix="/users",
        tags=["users"])

    return router
