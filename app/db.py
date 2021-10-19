import fastapi
import sqlmodel as sql
import sqlalchemy.engine

from app.settings import get_settings


_SQLALCHEMY_DATABASE_URL = get_settings().database_url or  "sqlite+pysqlite:///:memory:"

ENGINE = sql.create_engine(_SQLALCHEMY_DATABASE_URL)

Base = sql.SQLModel
Session = sql.Session


def get_engine() -> sqlalchemy.engine.Engine:
    return ENGINE


def get_session(engine: sqlalchemy.engine.Engine = fastapi.Depends(get_engine)) -> sql.Session:
    """
    Dependency -> SQLAlchemy `Session`. Usage:
        import fastapi
        import app.db as db
        
        @app.post("/foo/", response_model=schemas.Foo)
        def create_foo(foo: schemas.Foo, session: db.Session = fastapi.Depends(db.get_session)):
            # Use session
            pass
    """

    with sql.Session(engine) as session:
        yield session
