import fastapi
import sqlalchemy
import pydantic
from oso.oso import Oso

from fastapi_pagination import Page
from fastapi_pagination.ext.async_sqlalchemy import paginate

import app.db as db
import app.models as m
import app.auth as auth

import app.api.plants as plants


def make_router() -> fastapi.APIRouter:
    router = fastapi.APIRouter()

    @router.post("/activities", status_code=fastapi.status.HTTP_201_CREATED, response_model=m.Activity)
    async def create_activity(
        new_activity: m.NewActivity,
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)):

        result = await _create_activity(
            session=session,
            new_activity=new_activity,
            user=current_user,
            oso=oso
        )

        return result

    @router.get("/activities", response_model=Page[m.Activity])
    async def get_activities(
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)
    ):
        result = await _get_activities(
            session=session,
            user=current_user,
            oso=oso
        )

        return result

    @router.get("/activities/{idx}", response_model=m.Activity)
    async def get_activity(
        idx: int,
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)
    ):
        try:
            result = await _get_activity(
                idx,
                session=session,
                user=current_user,
                oso=oso
            )

            return result
        except sqlalchemy.exc.NoResultFound as exc:
            raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc

    @router.patch("/activities/{idx}", response_model=m.Activity)
    async def patch_planting(
        idx: int,
        activity_update: m.ActivityUpdate,
        current_user: m.User = fastapi.Depends(auth.current_user),
        session: db.Session = fastapi.Depends(db.get_async_session),
        oso: Oso = fastapi.Depends(auth.get_oso)
    ):
        try:
            result = await _patch_activity(
                idx,
                activity_update=activity_update,
                session=session,
                user=current_user,
                oso=oso
            )

            return result
        except sqlalchemy.exc.NoResultFound as exc:
            raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc
    
    return router

async def _create_activity(
    new_activity: m.NewActivity = None,
    user: m.User = None,
    session: db.Session = None,
    oso: Oso = None) -> m.Planting:
    
    # Authorize by checking Species for "write"
    try:
        species = await plants._get_species_idx(session,
                                                new_activity.species_id,
                                                user=user,
                                                oso=oso,
                                                action="write")
    except sqlalchemy.exc.NoResultFound as exc:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc
                    
    activity = m.Activity(zone_id=new_activity.zone_id, 
                          species=species,
                          description=new_activity.description,
                          short_description=new_activity.short_description)

    session.add(activity)

    await session.commit()
    await session.refresh(activity)

    return activity


async def _get_activities(
    user: m.User = None,
    session: db.Session = None,
    oso: Oso = None) -> list[m.Planting]:

    q = oso.authorized_query(user, "read", m.Activity)

    results = await paginate(session, q)
    
    return results

async def _get_activity(
    idx: int,
    user: m.User = None,
    session: db.Session = None,
    oso: Oso = None,
    action: str = "read") -> m.Activity:

    q = oso.authorized_query(user, action, m.Activity) \
            .where(m.Activity.id == idx)

    result = await session.execute(q)

    return result.scalars().one()

async def _patch_activity(
    idx: int,
    activity_update: m.ActivityUpdate,
    user: m.User = None,
    session: db.Session = None,
    oso: Oso = None) -> m.Activity:

    try:
        activity = await _get_activity(idx, session=session, user=user, oso=oso, action="write")
    except sqlalchemy.exc.NoResultFound as exc:
        raise fastapi.HTTPException(fastapi.status.HTTP_404_NOT_FOUND) from exc

    update_data = activity_update.dict(exclude_unset=True)
    for key,value in update_data.items():
        setattr(activity, key, value)
    
    session.add(activity)
    await session.commit()
    await session.refresh(activity)

    return activity
