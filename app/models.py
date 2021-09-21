
import uuid

import sqlalchemy
import sqlmodel as sql
import sqlalchemy.orm as orm

# from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
# from sqlalchemy.sql.sqltypes import INTEGER
from sqlalchemy.types import TypeDecorator, CHAR
# from sqlalchemy.dialects.postgresql import UUID

from typing import Optional, List

from app.db import Base
# import app.schemas as sk

# import fastapi_users

# class User(sk.User, fastapi_users.models.BaseUserDB):
#     pass


def create_all(engine: sqlalchemy.engine.Engine) -> None:
    """
    Create all tables
    """
    Base.metadata.create_all(bind=engine)


def drop_all(engine: sqlalchemy.engine.Engine) -> None:
    """
    !!Drop all the tables!!
    """

    Base.metadata.drop_all(bind=engine)


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(uuid.UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == "postgresql":
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return "%.32x" % uuid.UUID(value).int
            else:
                # hexstring
                return "%.32x" % value.int

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value

## Users and Teams

class User(Base, tabel=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True)
    full_name: Optional[str] = None
    username: str

    gardens: List["Garden"] = sql.Relationship(back_populates="owner")
    species: List["Species"] = sql.Relationship(back_populates="owner")
    plants: List["Plant"] = sql.Relationship(back_populates="owner")

# ## Business Model
class GardenBase(Base):
    name: str

class Garden(GardenBase, tabel=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True)

    owner: User = sql.Relationship(back_populates="gardens")
    plants: List["Plant"] = sql.Relationship(back_populates="gardens")

class Species(Base, tabel=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True)
    name: str

    owner: User = sql.Relationship(back_populates="species")


class Plant(Base, tabel=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True)
    name: str

    species: Species = sql.Relationship()
    gardens: List[Garden] = sql.Relationship(back_populates="plants")
    owner: User = sql.Relationship(back_populates="plants")
