import uuid
from pydantic import BaseModel

class User(BaseModel):
    class Config:
        orm_mode = True


## TEAM
class TeamBase(BaseModel):
    name: str

class TeamIn(TeamBase):
    pass

class TeamOut(TeamBase):
    id: int
    guid: uuid.UUID

    class Config:
        orm_mode = True


## GARDEN
class GardenBase(BaseModel):
    name: str

class GardenIn(GardenBase):
    pass

class GardenOut(GardenBase):
    id: int
    guid: uuid.UUID
    team_id: int



## SPECIES
class Species(BaseModel):
    id: int



## PLANT
class PlantBase(BaseModel):
    name: str

class PlantIn(PlantBase):
    species_id: int
    garden_id: int

class PlatOut(PlantBase):
    id: int