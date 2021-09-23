import fastapi
import oso
import app.db as db
import app.models as m


def _create_species(session: db.Session, owner: m.User = None, new_species: m.NewSpecies = None) -> m.Species:
    s = m.Species(name=new_species.name, owner=owner)
    session.add(s)
    session.commit()
    session.refresh(s)

    return s


def make_router(oso: oso.Oso) -> fastapi.APIRouter:
    router = fastapi.APIRouter()

    @router.post("/species", status_code=fastapi.status.HTTP_201_CREATED, response_model=m.Species)
    async def create_species(request: fastapi.Request, new_species: m.NewSpecies, session: db.Session = fastapi.Depends(db.get_session)):
        # if not oso.is_allowed(request.state.user, "create", new_species):
        #     raise fastapi.HTTPException(403)
        
        return _create_species(session, new_species=new_species)

    return router