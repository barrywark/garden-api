from typing import Optional

import fastapi
import sqlmodel as sql
from oso.oso import Oso

import app.db as db
import app.models as m
import app.auth as auth



async def _create_species(session: db.Session, 
                            owner: m.User = None, 
                            new_species: m.NewSpecies = None) -> m.Species:
    if owner is None:
        raise Exception("owner cannot be None")

    if new_species is None:
        raise Exception("new_species cannot be None")
    
    s = m.Species(name=new_species.name, owner=owner)
    session.add(s)
    await session.commit()

    return s


async def _get_species(session: db.Session, user: m.User = None) -> list[m.Species]:
    q = sql.select(m.Species) #.where(m.Species.owner_id == user.id)
    results = await session.execute(q)
    return results.all()

# def _get_species_idx(session: db.Session, idx: int, user: m.User = None) -> Optional[m.Species]:
#     return session.get(m.Species, idx) # TODO with owner_id


def make_router(oso: Oso) -> fastapi.APIRouter:
    router = fastapi.APIRouter()

    @router.post("/species", status_code=fastapi.status.HTTP_201_CREATED, response_model=m.Species)
    async def create_species(new_species: m.NewSpecies, 
                             current_user: m.User = fastapi.Depends(auth.current_user), 
                             session: db.Session = fastapi.Depends(db.get_async_session)):
        
        if not oso.is_allowed(current_user, "create", new_species):
            raise fastapi.HTTPException(fastapi.status.HTTP_403_FORBIDDEN)
        
        return await _create_species(session, new_species=new_species, owner=current_user)

    @router.get("/species", response_model=list[m.Species])
    async def get_species(current_user: m.User = fastapi.Depends(auth.current_user),
                        session: db.Session = fastapi.Depends(db.get_async_session)):
        
        return await _get_species(session, user=current_user)


    @router.get("/species/{idx}", response_model=m.Species)
    async def get_species_id(idx: int, 
                             current_user: m.User = fastapi.Depends(auth.current_user), 
                             session: db.Session = fastapi.Depends(db.get_async_session)):
        
        user = session.get(m.User, current_user.id)
        s = _get_species_idx(session, idx, user=user)
        if s is None:
            raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)

        return s

    return router
