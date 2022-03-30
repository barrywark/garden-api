from typing import Optional, List
import uuid
import pydantic

import sqlmodel as sql
import fastapi_users.models
import fastapi_users_db_sqlmodel as users_sqlmodel

Base = sql.SQLModel

class DeleteModel(Base, table=False):
    ok: bool

#region Users
class UserModel(fastapi_users.models.BaseUser):
    pass


class UserCreateModel(fastapi_users.models.BaseUserCreate):
    pass


class UserUpdateModel(fastapi_users.models.BaseUserUpdate):
    pass


class User(users_sqlmodel.SQLModelBaseUserDB, table=True):
    # Override to add index
    id: pydantic.UUID4 = sql.Field(default_factory=uuid.uuid4,
                                    primary_key=True,
                                    nullable=False,
                                    index=True)

    species: Optional[List["Species"]] = sql.Relationship(back_populates="owner")
    gardens: Optional[List["Garden"]] = sql.Relationship(back_populates="owner")

#endregion


#region Business Model
class GardenBase(Base):
    name: str

class Garden(GardenBase, table=True):
    id: Optional[pydantic.UUID4] = sql.Field(default_factory=uuid.uuid4,
                                    primary_key=True,
                                    nullable=False,
                                    index=True)

    owner_id: pydantic.UUID4 = sql.Field(default_factory=None, foreign_key="user.id")
    owner: User = sql.Relationship(back_populates="gardens")

    plantings: Optional[List["Planting"]] = sql.Relationship(back_populates="garden")

#region Species
class NewSpecies(Base):
    name: str

class SpeciesUpdate(Base):
    name: Optional[str] = None
    # owner_id: Optional[pydantic.UUID4]


class Species(NewSpecies, table=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True, nullable=False)
    name: str

    owner_id: pydantic.UUID4 = sql.Field(default_factory=None, foreign_key="user.id")
    owner: User = sql.Relationship(back_populates="species")
#endregion

class Planting(Base, table=True):
    id: pydantic.UUID4 = sql.Field(default_factory=uuid.uuid4,
                                    primary_key=True,
                                    nullable=False,
                                    index=True)

    species_id: int = sql.Field(foreign_key="species.id")
    species: Species = sql.Relationship()

    garden_id: pydantic.UUID4 = sql.Field(default_factory=None, foreign_key="garden.id")
    garden: Garden = sql.Relationship(back_populates="plantings")


class Zone(Base, table=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True, nullable=False)
    name: str
#endregion