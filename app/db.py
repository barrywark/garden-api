import os

import sqlmodel as sql

from app.settings import get_settings


_SQLALCHEMY_DATABASE_URL = get_settings().database_url or  "sqlite+pysqlite:///:memory:"

ENGINE = sql.create_engine(_SQLALCHEMY_DATABASE_URL)

Base = sql.SQLModel
Session = sql.Session

def get_session() -> sql.Session:
    """
    Dependency -> SQLAlchemy `Session`. Usage:
        import fastapi
        import app.db as db
        
        @app.post("/foo/", response_model=schemas.Foo)
        def create_foo(foo: schemas.Foo, db: db.Session = fastapi.Depends(db.get_session)):
            # Use db
            pass
    """

    with sql.Session(ENGINE) as session:
        yield session