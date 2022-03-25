from typing import Optional

import fastapi
import sqlalchemy
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


async def _get_species(session: db.Session, user: m.User = None, oso: Oso = None) -> list[m.Species]:
    q = sql.select(m.Species).where(m.Species.owner == user)
    # oso_q = oso.authorized_query(user, "read", m.Species)

    results = await session.execute(q)
    return results.scalars().all()

async def _get_species_idx(session: db.Session, 
                            idx: int,
                            user: m.User = None) -> Optional[m.Species]:
    
    q = sql.select(m.Species) \
        .where(m.Species.id == idx) \
        .where(m.Species.owner == user)
    
    result = await session.execute(q) # TODO with owner_id
    return result.scalars().one()


def make_router() -> fastapi.APIRouter:
    router = fastapi.APIRouter()

    @router.post("/species", status_code=fastapi.status.HTTP_201_CREATED, response_model=m.Species)
    async def create_species(new_species: m.NewSpecies, 
                             current_user: m.User = fastapi.Depends(auth.current_user), 
                             session: db.Session = fastapi.Depends(db.get_async_session),
                             oso: Oso = fastapi.Depends(auth.get_oso)):
        
        if not oso.is_allowed(current_user, "create", m.Species):
            raise fastapi.HTTPException(fastapi.status.HTTP_403_FORBIDDEN)
        
        result = await _create_species(session, new_species=new_species, owner=current_user)
        return result


    @router.get("/species", response_model=list[m.Species])
    async def get_species(current_user: m.User = fastapi.Depends(auth.current_user),
                        session: db.Session = fastapi.Depends(db.get_async_session),
                        oso: Oso = fastapi.Depends(auth.get_oso)):
        
        result = await _get_species(session, user=current_user, oso=oso)
        return result


    @router.get("/species/{idx}", response_model=m.Species)
    async def get_species_id(idx: int, 
                             current_user: m.User = fastapi.Depends(auth.current_user), 
                             session: db.Session = fastapi.Depends(db.get_async_session)):
        
        try:
            result = await _get_species_idx(session, idx, user=current_user)
            return result
        except sqlalchemy.exc.NoResultFound:
            raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)
        

    return router
