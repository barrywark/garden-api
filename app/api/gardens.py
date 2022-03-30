from typing import Optional

import fastapi
import sqlalchemy
import pydantic
from oso.oso import Oso

import app.db as db
import app.models as m
import app.auth as auth

def make_router() -> fastapi.APIRouter:
    router = fastapi.APIRouter()

    @router.post("/gardens", status_code=fastapi.status.HTTP_201_CREATED, response_model=m.Garden)
    async def create_garden(
        new_garden: m.NewGarden,
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)):

        oso.authorize(current_user, "create", m.Garden)

        result = await _create_garden(
            session=session,
            new_garden=new_garden,
            owner=current_user
        )

        return result

    @router.get("/gardens", response_model=list[m.Garden])
    async def get_gardens(
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)):
        
        result = await _get_gardens(
            session=session,
            user=current_user,
            oso=oso
        )

        return result

    @router.get("/gardens/{idx}", response_model=m.Garden)
    async def get_garden(
        idx: pydantic.UUID4,
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)
    ):
        result = await _get_garden(
            idx,
            session=session,
            user=current_user,
            oso=oso
        )

        return result

    @router.patch("/gardens/{idx}", response_model=m.Garden)
    async def patch_garden(
        idx: pydantic.UUID4,
        garden_update: m.GardenUpdate,
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)
    ):
        result = await _patch_garden(
            idx,
            garden_update=garden_update,
            session=session,
            user=current_user,
            oso=oso
        )

        return result
    

    return router

async def _create_garden(
    new_garden: m.NewGarden = None,
    owner: m.User = None,
    session: db.Session = None) -> m.Garden:
    
    garden = m.Garden(owner=owner, name=new_garden.name)

    session.add(garden)
    await session.commit()
    await session.refresh(garden)

    return garden


async def _get_gardens(
    user: m.User = None,
    session: db.Session = None,
    oso: Oso = None) -> list[m.Garden]:

    q = oso.authorized_query(user, "read", m.Garden)

    results = await session.execute(q)
    
    return results.scalars().all()


async def _get_garden(
    idx: pydantic.UUID4,
    user: m.User = None,
    session: db.Session = None,
    oso: Oso = None,
    action: str = "read") -> m.Garden:

    q = oso.authorized_query(user, action, m.Garden) \
            .where(m.Garden.id == idx)

    result = await session.execute(q)

    return result.scalars().one()

async def _patch_garden(
    idx: pydantic.UUID4,
    garden_update: m.GardenUpdate,
    user: m.User = None,
    session: db.Session = None,
    oso: Oso = None) -> m.Garden:

    try:
        garden = await _get_garden(idx, session=session, user=user, oso=oso, action="write")
    except sqlalchemy.exc.NoResultFound as exc:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc

    update_data = garden_update.dict(exclude_unset=True)
    for key,value in update_data.items():
        setattr(garden, key, value)
    
    session.add(garden)
    await session.commit()
    await session.refresh(garden)

    return garden
