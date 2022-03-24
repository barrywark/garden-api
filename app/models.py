from typing import Optional

import sqlmodel as sql
import fastapi_users.models
import fastapi_users_db_sqlmodel as users_sqlmodel

Base = sql.SQLModel

## Users
class UserModel(fastapi_users.models.BaseUser):
    pass


class UserCreateModel(fastapi_users.models.BaseUserCreate):
    pass


class UserUpdateModel(fastapi_users.models.BaseUserUpdate):
    pass


class User(users_sqlmodel.SQLModelBaseUserDB, table=True):
    pass

# ## Business Model
class GardenBase(Base):
    name: str

class Garden(GardenBase, table=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True, nullable=False)

    #owner: User = sql.Relationship(back_populates="gardens")
    #plants: List["Plant"] = sql.Relationship(back_populates="gardens")

class NewSpecies(Base):
    name: str

class Species(NewSpecies, table=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True, nullable=False)
    name: str

    # owner_id: int = sql.Field(default=None, foreign_key="user.id")
    # owner: User = sql.Relationship(back_populates="species")


class Plant(Base, table=True):
    id: Optional[int] = sql.Field(default=None, primary_key=True, nullable=False)
    name: str

    #species: Species = sql.Relationship()
    #gardens: List[Garden] = sql.Relationship(back_populates="plants")
    #owner: User = sql.Relationship(back_populates="plants")
