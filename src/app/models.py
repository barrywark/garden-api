
import uuid

import sqlalchemy as sql
import sqlalchemy
import sqlalchemy.orm as orm

from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.sql.sqltypes import INTEGER
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


def create_all(engine: sqlalchemy.engine.Engine) -> None:
    """
    Create all tables
    """
    Base.metadata.create_all(bind=engine)


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(UUID())
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
class UserTeam(Base):
    __tablename__ = "users_teams"
    id = Column(Integer, primary_key=True)

    user_id = Column(Integer, ForeignKey("users.id"))
    team_id = Column(Integer, ForeignKey("teams.id"))



class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    fullname = Column(String)
    guid = Column(GUID(), default=uuid.uuid4, unique=True)

    teams = orm.relationship("Team",
                    secondary="users_teams",
                    backref="members")


    def __repr__(self):
        return f"User(id={self.id!r}, guid={self.guid}, fullname={self.fullname!r}, email={self.email!r})"



class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    guid = Column(GUID(), default=uuid.uuid4, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    # members created via User.teams backref
    owner = orm.relationship("User")
    gardens = orm.relationship("Garden", order_by="Garden.id", back_populates="team")

    def __repr__(self) -> str:
        return f"Team(id={self.id!r}, guid={self.guid!r}, name={self.name!r})"



## Business Model
class Garden(Base):
    __tablename__ = "gardens"

    id = Column(Integer, primary_key=True)
    guid = Column(GUID(), default=uuid.uuid4, unique=True)
    team_id = Column(Integer, ForeignKey("teams.id"))

    team = orm.relationship("Team", back_populates="gardens")
    plants = orm.relationship("Plant", back_populates="garden")


    def __repr__(self) -> str:
        return f"Garden(id={self.id!r}, guid={self.guid!r})"


class Plant(Base):
    __tablename__ = "plants"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    garden_id = Column(Integer, ForeignKey("gardens.id")) 
    species_id = Column(Integer, ForeignKey("species.id"))

    garden = orm.relationship("Garden", back_populates="plants")
    species = orm.relationship("Species")


class Species(Base):
    __tablename__ = "species"

    id = Column(Integer, primary_key=True)

    