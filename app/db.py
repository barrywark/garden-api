import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

from app.settings import get_settings

import sqlalchemy.orm as orm


# TODO
#"postgresql://user:password@postgresserver/db"
_SQLALCHEMY_DATABASE_URL = get_settings().database_url or  "sqlite:///./gardenapi.db"

ENGINE = create_engine(_SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

_SESSION_MAKER = orm.sessionmaker(autocommit=False, autoflush=False, bind=ENGINE)

Base = declarative_base()

def get_db() -> orm.Session:
    """
    Dependency -> SQLAlchemy `Session`. Usage:
        import fastapi
        import app.db as db
        import sqlalchemy.orm as orm
        
        @app.post("/foo/", response_model=schemas.Foo)
        def create_foo(foo: schemas.Foo, db: orm.Session = fastapi.Depends(db.get_db)):
            # Use db
            pass
    """

    with _SESSION_MAKER() as session:
        yield session

