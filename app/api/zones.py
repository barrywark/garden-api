from typing import Optional

import fastapi
import sqlalchemy
from oso.oso import Oso

import app.db as db
import app.models as m
import app.auth as auth

def make_router() -> fastapi.APIRouter:
    router = fastapi.APIRouter()

    @router.post("/zones", status_code=fastapi.status.HTTP_201_CREATED, response_model=m.Zone)
    async def create_zone(
        new_zone: m.Zone,
        current_user: m.User= fastapi.Depends(auth.current_super_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)):

        result = await _create_zone(
            session=session, 
            new_zone=new_zone,
            owner=current_user,
            oso=oso)
        
        return result
    

    return router


async def _create_zone(
    session: db.Session = None,
    new_zone: m.Zone = None,
    owner: m.User = None,
    oso: Oso = None) -> m.Zone:

    z = m.Zone(owner=owner, name=new_zone.name)
    oso.authorize(owner, "create", z)

    session.add(z)
    await session.commit()
    await session.refresh(z)

    return z