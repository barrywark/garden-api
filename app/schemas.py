import uuid
from typing import Optional
from pydantic import BaseModel

from fastapi_users import models


class User(models.BaseUser):
    pass


class UserCreate(models.BaseUserCreate):
    pass


class UserUpdate(User, models.BaseUserUpdate):
    pass


## TEAM
class TeamBase(BaseModel):
    name: str
    owner: User
    members: Optional[list[User]] = None

class TeamIn(TeamBase):
    pass

class TeamOut(TeamBase):
    id: int
    guid: uuid.UUID

    class Config:
        orm_mode = True



## SPECIES
class Species(BaseModel):
    id: int
    name: str


## PLANT
class PlantBase(BaseModel):
    name: str
    species: Species
    garden_id: int

class PlantIn(PlantBase):
    pass

class PlantOut(PlantBase):
    id: int


## GARDEN
class GardenBase(BaseModel):
    name: str
    team_id: int

class GardenIn(GardenBase):
    pass

class GardenOut(GardenBase):
    id: int
    guid: uuid.UUID

    plants: Optional[list[PlantOut]] = None