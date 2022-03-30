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

    @router.get("/zones", response_model=list[m.Zone])
    async def get_zones(
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)):

        result = await _get_zones(
            session=session,
            user=current_user,
            oso=oso
        )

        return result

    @router.patch("/zones/{idx}", response_model=m.Zone)
    async def patch_zone(
        idx: int,
        patch_zone: m.ZoneUpdate,
        current_user: m.User = fastapi.Depends(auth.current_super_user), 
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)):

        result = await _patch_zone(
            idx,
            patch_zone=patch_zone,
            user=current_user,
            session=session,
            oso=oso
        )

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

async def _get_zones(
    session: db.Session = None,
    user: m.User = None,
    oso: Oso = None) -> list[m.Zone]:
    
    q = oso.authorized_query(user, "read", m.Zone)

    results = await session.execute(q)
    
    return results.scalars().all()

async def _patch_zone(
    idx: int,
    patch_zone: m.Zone =None,
    user: m.User = None,
    session: db.Session = None,
    oso: Oso = None
) -> m.Zone:

    try:
        zone = await _get_zone(idx, session=session, user=user, oso=oso, action="write")
    except sqlalchemy.exc.NoResultFound as exc:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc
    
    # update
    update_data = patch_zone.dict(exclude_unset=True)
    for key,value in update_data.items():
        setattr(zone, key, value)
    
    # commit
    session.add(zone)
    await session.commit()
    await session.refresh(zone)
    
    return zone


async def _get_zone(
    idx: int,
    session: db.Session = None, 
    user: m.User = None,
    oso: Oso = None,
    action: str = "read") -> Optional[m.Zone]:
    
    q = oso.authorized_query(user, action, m.Zone) \
            .where(m.Zone.id == idx)
    
    result = await session.execute(q)
    return result.scalars().one()