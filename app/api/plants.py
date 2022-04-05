from typing import Optional

import fastapi
import sqlalchemy
from oso.oso import Oso

from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate

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


async def _get_species(session: db.Session, 
    user: m.User = None, 
    oso: Oso = None) -> list[m.Species]:

    q = oso.authorized_query(user, "read", m.Species)

    return await paginate(session, q)

async def _get_species_idx(session: db.Session, 
                            idx: int,
                            user: m.User = None,
                            oso: Oso = None,
                            action: str = "read") -> Optional[m.Species]:
    
    q = oso.authorized_query(user, action, m.Species) \
            .where(m.Species.id == idx)
    
    result = await session.execute(q)
    return result.scalars().one()

async def _patch_species(session: db.Session,
                        idx: int,
                        patch_species: m.SpeciesUpdate = None,
                        user: m.User = None,
                        oso: Oso = None) -> Optional[m.Species]:

    try:
        species = await _get_species_idx(session, idx, user=user, oso=oso, action="write")
    except sqlalchemy.exc.NoResultFound as exc:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc
    
    # update
    update_data = patch_species.dict(exclude_unset=True)
    for key,value in update_data.items():
        setattr(species, key, value)
    
    # commit
    session.add(species)
    await session.commit()
    await session.refresh(species)
    
    return species


async def _delete_species(session: db.Session,
                        idx: int,
                        user: m.User = None,
                        oso: Oso = None) -> m.DeleteModel:
    
    try:
        species = await _get_species_idx(session, idx, user=user, oso=oso, action="delete")
    except sqlalchemy.exc.NoResultFound as exc:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc
    
    session.delete(species)
    await session.commit()

    return m.DeleteModel(ok=True)


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


    @router.get("/species", response_model=Page[m.Species])
    async def get_species(current_user: m.User = fastapi.Depends(auth.current_user),
                        session: db.Session = fastapi.Depends(db.get_async_session),
                        oso: Oso = fastapi.Depends(auth.get_oso)):
        
        result = await _get_species(session, user=current_user, oso=oso)
        return result


    @router.get("/species/{idx}", response_model=m.Species)
    async def get_species_id(idx: int, 
                             current_user: m.User = fastapi.Depends(auth.current_user), 
                             session: db.Session = fastapi.Depends(db.get_async_session),
                             oso: Oso = fastapi.Depends(auth.get_oso)):
        
        try:
            result = await _get_species_idx(session, idx, user=current_user, oso=oso)
            return result
        except sqlalchemy.exc.NoResultFound as exc:
            raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc
        
    
    @router.patch("/species/{idx}", response_model=m.Species)
    async def patch_species_idx(idx: int,
                             patch_species: m.SpeciesUpdate,
                             current_user: m.User = fastapi.Depends(auth.current_user), 
                             session: db.Session = fastapi.Depends(db.get_async_session),
                             oso: Oso = fastapi.Depends(auth.get_oso)):
        
        result = await _patch_species(
            session,
            idx,
            patch_species=patch_species,
            user=current_user,
            oso=oso)

        return result

    @router.delete("/species/{idx}", response_model=m.DeleteModel)
    async def delete_species(idx: int,
                            current_user: m.User = fastapi.Depends(auth.current_user), 
                            session: db.Session = fastapi.Depends(db.get_async_session),
                            oso: Oso = fastapi.Depends(auth.get_oso)):

        result = await _delete_species(
            session,
            idx,
            user=current_user,
            oso=oso
        )

        return result
    

    return router
