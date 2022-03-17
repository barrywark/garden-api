import uuid
from jinja2 import pass_context
import sqlalchemy
import sqlmodel as sql
import fastapi_users.models

from typing import AsyncGenerator
from typing import Optional, List
from sqlalchemy.types import TypeDecorator, CHAR

Base = sql.SQLModel

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


## Users
class User(fastapi_users.models.BaseUser):
    pass


class UserCreate(fastapi_users.models.BaseUserCreate):
    pass


class UserUpdate(fastapi_users.models.BaseUserUpdate):
    pass


class UserDB(User, fastapi_users.models.BaseUserDB):
     #gardens: List["Garden"] = sql.Relationship(back_populates="owner")
     #species: List["Species"] = sql.Relationship(back_populates="owner")
     #plants: List["Plant"] = sql.Relationship(back_populates="owner")
     pass


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

    # owner_id: int = sql.Field(default=None, foreign_key="user.id")
    # owner: User = sql.Relationship(back_populates="species")


class Plant(Base, table=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True)
    name: str

    #species: Species = sql.Relationship()
    #gardens: List[Garden] = sql.Relationship(back_populates="plants")
    #owner: User = sql.Relationship(back_populates="plants")
