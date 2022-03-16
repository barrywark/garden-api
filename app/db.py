import sqlmodel as sql

from typing import AsyncGenerator

from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine

from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
    SQLAlchemyBaseAccessTokenTable,
)


from app.models import UserDB

from app.settings import get_settings

_SQLALCHEMY_DATABASE_URL = get_settings().database_url or  "sqlite+pysqlite:///:memory:"

Base = sql.SQLModel
DeclarativeBase: DeclarativeMeta = declarative_base()

_ENGINE = create_async_engine(_SQLALCHEMY_DATABASE_URL)
async_session_maker = sessionmaker(_ENGINE, class_=AsyncSession, expire_on_commit=False)

class UserTable(DeclarativeBase, SQLAlchemyBaseUserTable):
    pass

class AccessTokenTable(SQLAlchemyBaseAccessTokenTable, Base):
    pass

async def create_db_and_tables():
    async with _ENGINE.begin() as conn:
        await conn.run_sync(DeclarativeBase.metadata.create_all)
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
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


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    """
    Get fastapi-users `UserDatabase`
    """
    yield SQLAlchemyUserDatabase(UserDB, session, UserTable)

async def get_engine() -> AsyncGenerator[AsyncEngine, None]:
    yield _ENGINE