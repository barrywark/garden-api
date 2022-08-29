from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users_db_sqlmodel import SQLModelUserDatabaseAsync
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine

import app.models as models

from app.settings import get_settings, Settings

Session = AsyncSession

_ENGINE = None


def get_engine(settings: Settings = Depends(get_settings)) -> AsyncEngine:
    """
    Async dependency for database engine
    """

    global _ENGINE

    if _ENGINE is None:
        _ENGINE = create_async_engine(settings.database_url)

    return _ENGINE


_ASYNC_SESSION_MAKER = None


def get_async_session_maker(engine: AsyncEngine = Depends(get_engine)):
    """
    Get an async session maker
    """

    global _ASYNC_SESSION_MAKER

    if _ASYNC_SESSION_MAKER is None:
        _ASYNC_SESSION_MAKER = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    return _ASYNC_SESSION_MAKER


_SYNC_SESSION_MAKER = None


def get_sync_session_maker(engine: AsyncEngine = Depends(get_engine)):
    global _SYNC_SESSION_MAKER

    if _SYNC_SESSION_MAKER is None:
        _SYNC_SESSION_MAKER = sessionmaker(engine, expire_on_commit=False)

    return _SYNC_SESSION_MAKER


async def get_async_session(async_session_maker=Depends(get_async_session_maker)) -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency -> SQLAlchemy `Session`. Usage:
        import fastapi
        import app.db as db
        
        @app.post("/foo/", response_model=schemas.Foo)
        def create_foo(foo: schemas.Foo, session: db.Session = fastapi.Depends(db.get_async_session)):
            # Use session
            pass
    """
    async with async_session_maker() as session:
        yield session


async def get_sync_session(sync_session_maker=Depends(get_sync_session_maker)) -> AsyncGenerator[Session, None]:
    with sync_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)) -> AsyncGenerator[SQLModelUserDatabaseAsync, None]:
    """
    Get fastapi-users `UserDatabase`
    """
    yield SQLModelUserDatabaseAsync(session,
                                    models.User)


async def create_db_and_tables(engine: AsyncEngine = Depends(get_engine)):
    """
    Create database tables
    """

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)


async def drop_tables(engine: AsyncEngine = Depends(get_engine)):
    """
    Drop database tables
    """

    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.drop_all)
