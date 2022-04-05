import fastapi
import sqlalchemy
import pydantic
from oso.oso import Oso

from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate

import app.db as db
import app.models as m
import app.auth as auth
import app.api.gardens as gardens
import app.api.plants as plants

def make_router() -> fastapi.APIRouter:
    router = fastapi.APIRouter()

    @router.post("/plantings", status_code=fastapi.status.HTTP_201_CREATED, response_model=m.Planting)
    async def create_planting(
        new_planting: m.NewPlanting,
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)):

        result = await _create_planting(
            session=session,
            new_planting=new_planting,
            user=current_user,
            oso=oso
        )

        return result

    @router.get("/plantings", response_model=Page[m.Planting])
    async def get_plantings(
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)):
        
        result = await _get_plantings(
            session=session,
            user=current_user,
            oso=oso
        )

        return result

    @router.get("/plantings/{idx}", response_model=m.Planting)
    async def get_planting(
        idx: pydantic.UUID4,
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)
    ):
        try:
            result = await _get_planting(
                idx,
                session=session,
                user=current_user,
                oso=oso
            )
        except sqlalchemy.exc.NoResultFound as exc:
            raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc

        return result

    @router.patch("/plantings/{idx}", response_model=m.Planting)
    async def patch_planting(
        idx: pydantic.UUID4,
        planting_update: m.PlantingUpdate,
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)
    ):
        try:
            result = await _patch_planting(
                idx,
                planting_update=planting_update,
                session=session,
                user=current_user,
                oso=oso
            )
        except sqlalchemy.exc.NoResultFound as exc:
            raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc

        return result
    

    return router

async def _create_planting(
    new_planting: m.NewPlanting = None,
    user: m.User = None,
    session: db.Session = None,
    oso: Oso = None) -> m.Planting:
    
    # Authorize by checking Garden for "write" and Species for "read"
    try:
        garden = await gardens._get_garden(new_planting.garden_id,
                                        session=session,
                                        user=user,
                                        oso=oso,
                                        action="write")

        species = await plants._get_species_idx(session,
                                                new_planting.species_id,
                                                user=user,
                                                oso=oso,
                                                action="read")
    except sqlalchemy.exc.NoResultFound as exc:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc
                    
    planting = m.Planting(garden=garden, 
                          species=species)

    session.add(planting)

    await session.commit()
    await session.refresh(planting)

    return planting


async def _get_plantings(
    user: m.User = None,
    session: db.Session = None,
    oso: Oso = None) -> list[m.Planting]:

    q = oso.authorized_query(user, "read", m.Planting)

    results = await paginate(session, q)
    
    return results


async def _get_planting(
    idx: pydantic.UUID4,
    user: m.User = None,
    session: db.Session = None,
    oso: Oso = None,
    action: str = "read") -> m.Planting:

    q = oso.authorized_query(user, action, m.Planting) \
            .where(m.Planting.id == idx)

    result = await session.execute(q)

    return result.scalars().one()

async def _patch_planting(
    idx: pydantic.UUID4,
    planting_update: m.PlantingUpdate,
    user: m.User = None,
    session: db.Session = None,
    oso: Oso = None) -> m.Planting:

    try:
        planting = await _get_planting(idx, session=session, user=user, oso=oso, action="write")
    except sqlalchemy.exc.NoResultFound as exc:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc

    update_data = planting_update.dict(exclude_unset=True)
    for key,value in update_data.items():
        setattr(planting, key, value)
    
    session.add(planting)
    await session.commit()
    await session.refresh(planting)

    return planting
