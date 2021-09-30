import fastapi
import oso
import app.db as db
import app.auth as auth
import app.models as m
import sqlmodel as sql

from typing import Optional


def _create_species(session: db.Session, owner: m.User = None, new_species: m.NewSpecies = None) -> m.Species:
    s = m.Species(name=new_species.name, owner=owner)
    session.add(s)
    session.commit()
    session.refresh(s)

    return s


def _get_species(session: db.Session) -> list[m.Species]:
    stmt = sql.select(m.Species)
    return session.exec(stmt).all()

def _get_species_idx(session: db.Session, id: int) -> Optional[m.Species]:
    return session.get(m.Species, id)


def make_router(oso: oso.Oso) -> fastapi.APIRouter:
    router = fastapi.APIRouter()

    @router.post("/species", status_code=fastapi.status.HTTP_201_CREATED, response_model=m.Species)
    async def create_species(request: fastapi.Request, new_species: m.NewSpecies, session: db.Session = fastapi.Depends(db.get_session)):
        # if not oso.is_allowed(request.state.user, "create", new_species):
        #     raise fastapi.HTTPException(403)
        
        return _create_species(session, new_species=new_species)

    @router.get("/species", response_model=list[m.Species])
    async def get_species(request: fastapi.Request, session: db.Session = fastapi.Depends(db.get_session)):
        return _get_species(session)


    @router.get("/species/{id}", response_model=m.Species)
    async def get_species_id(request: fastapi.Request, id: int, session: db.Session = fastapi.Depends(db.get_session)):
        s = _get_species_idx(session, id)
        if s is None:
            raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND)

        return s

    return router
