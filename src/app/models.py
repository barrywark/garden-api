
import uuid

import sqlalchemy as sql
import sqlalchemy.orm as orm

from sqlalchemy import Column, String, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.dialects.postgresql import UUID

from app.db import Base


def create_all(engine):
    Base.metadata.create_all(bind=engine)


class GUID(TypeDecorator):
    """Platform-independent GUID type.

    Uses PostgreSQL's UUID type, otherwise uses
    CHAR(32), storing as stringified hex values.

    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(32))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
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
    __tablename__ = 'users_teams'
    id = Column(Integer, primary_key=True)

    roles = Column(String) # Enum 'admin'|'member'
    user_id = Column(GUID(), ForeignKey('users.id'))
    team_id = Column(GUID(), ForeignKey('teams.id'))



class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String)
    fullname = Column(String)
    guid = GUID()

    UniqueConstraint('email', name='user_email_idx')
    UniqueConstraint('guid', name='user_guid_idx')

    teams = orm.relationship("Team",
                    secondary="users_teams",
                    backref="members")


    def __repr__(self):
        return f"User(id={self.id!r}, guid={self.guid}, fullname={self.fullname!r}, email={self.email!r})"



class Team(Base):
    __tablename__ = 'teams'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    guid = GUID()

    # members created via User.teams backref

    def __repr__(self) -> str:
        return f"Team(id={self.id!r}, guid={self.guid!r}, name={self.name!r})"



## Business Model
class Garden(Base):
    __tablename__ = 'gardens'

    id = Column(Integer, primary_key=True)
    guid = GUID()

    def __repr__(self) -> str:
        return f"Garden(id={self.id!r}, guid={self.guid!r})"