
import uuid

import sqlalchemy
import sqlmodel as sql
import sqlalchemy.orm as orm

from sqlalchemy.types import TypeDecorator, CHAR

from typing import Optional, List

from app.db import Base



def create_all(engine: sqlalchemy.engine.Engine) -> None:
    """
    Create all tables
    """
    Base.metadata.create_all(engine)


def drop_all(engine: sqlalchemy.engine.Engine) -> None:
    """
    !!Drop all the tables!!
    """

    Base.metadata.drop_all(engine)


class AuthToken(Base, table=False):
    token: str

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

class UserBase(Base):
    full_name: Optional[str] = None
    email: str


class User(UserBase, table=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True)

    #gardens: List["Garden"] = sql.Relationship(back_populates="owner")
    species: List["Species"] = sql.Relationship(back_populates="owner")
    #plants: List["Plant"] = sql.Relationship(back_populates="owner")

# ## Business Model
class GardenBase(Base):
    name: str

class Garden(GardenBase, table=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True)

    #owner: User = sql.Relationship(back_populates="gardens")
    #plants: List["Plant"] = sql.Relationship(back_populates="gardens")

class NewSpecies(Base):
    name: str

class Species(NewSpecies, table=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True)
    name: str

    owner_id: int = sql.Field(default=None, foreign_key="user.id")
    owner: User = sql.Relationship(back_populates="species")


class Plant(Base, table=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True)
    name: str

    #species: Species = sql.Relationship()
    #gardens: List[Garden] = sql.Relationship(back_populates="plants")
    #owner: User = sql.Relationship(back_populates="plants")
