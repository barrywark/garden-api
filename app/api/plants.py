import fastapi
import app.db as db
import app.auth as auth
import app.models as m
import sqlmodel as sql

from typing import Optional
from oso import Oso


def _create_species(session: db.Session, owner: m.User = None, new_species: m.NewSpecies = None) -> m.Species:
    s = m.Species(name=new_species.name, owner=owner)
    session.add(s)
    session.commit()
    session.refresh(s)

    return s


def _get_species(session: db.Session, user: m.User = None) -> list[m.Species]:
    return session.query(m.Species).where(m.Species.owner_id == user.id).all()

def _get_species_idx(session: db.Session, idx: int, user: m.User = None) -> Optional[m.Species]:
    return session.get(m.Species, idx)


def make_router(oso: Oso) -> fastapi.APIRouter:
    router = fastapi.APIRouter()

    @router.post("/species", status_code=fastapi.status.HTTP_201_CREATED, response_model=m.Species)
    async def create_species(new_species: m.NewSpecies, 
                             current_user: m.SerializedUser = fastapi.Depends(auth.current_user), 
                             session: db.Session = fastapi.Depends(db.get_session)):
        user = session.get(m.User, current_user.id)
        if not oso.is_allowed(user, "create", new_species):
            raise fastapi.HTTPException(fastapi.status.HTTP_403_FORBIDDEN)
        
        return _create_species(session, new_species=new_species, owner=user)

    @router.get("/species", response_model=list[m.Species])
    async def get_species(current_user: m.SerializedUser = fastapi.Depends(auth.current_user),
                        session: db.Session = fastapi.Depends(db.get_session)):
        user = session.get(m.User, current_user.id)
        
        return _get_species(session, user=user)


    @router.get("/species/{idx}", response_model=m.Species)
    async def get_species_id(idx: int, 
                             current_user: m.SerializedUser = fastapi.Depends(auth.current_user), 
                             session: db.Session = fastapi.Depends(db.get_session)):
        
        user = session.get(m.User, current_user.id)
        s = _get_species_idx(session, idx, user=user)
        if s is None:
            raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)

        return s

    return router
