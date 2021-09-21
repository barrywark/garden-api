import fastapi

import app.db as db
import app.models as m


def create_species(session: db.Session, owner: m.User, name: str) -> m.Species:
    s = m.Species(name=name, owner=owner)
    session.add(s)
    session.commit()
    session.refresh(s)

    return s


def make_router() -> fastapi.APIRouter:
    router = fastapi.APIRouter()

    @router.post("/species")
    async def create_species(name:str,
                            owner: m.User,
                            db: db.Session = fastapi.Depends(db.get_session)):
        
        return {}

    return router