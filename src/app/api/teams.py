import uuid

import sqlalchemy as sql
import sqlalchemy.orm as orm
import app.models as m
import app.schemas as sk
import app.db as db

import fastapi_users

from fastapi import Depends, APIRouter
from fastapi.exceptions import HTTPException

def get_team_by_guid(db: orm.Session, team_guid: uuid.UUID) -> m.Team:
    return db.query(m.Team).filter(m.Team.guid == team_guid).one_or_none()

def get_team_by_id(db: orm.Session, team_id: int) -> m.Team:
    return db.query(m.Team).filter(m.Team.id == team_id).one_or_none()


def create_team(db: orm.Session, owner: m.User, name: str) -> m.Team:
    team = m.Team(name=name, owner=owner)
    team.members.append(owner)
    db.add(team)
    db.commit()

    return team

def delete_team(db: orm.Session, team: m.Team) -> None:
    db.delete(team)
    db.commit()


def add_member(db:orm.Session, team: m.Team, member: m.User) -> None:
    team.members.append(member)


def remove_member(db: orm.Session, team: m.Team, member: m.User) -> None:
    team.members.remove(member)


def make_router(users: fastapi_users.FastAPIUsers) -> APIRouter:
    router = APIRouter()

    @router.get("/teams/{id}")
    async def get_team(id: int,
                        current_user: sk.User = Depends(users.current_user(active=True)),
                        db: orm.Session = Depends(db.get_db)):
        
        team = get_team_by_id(db, id)
        if not (team.owner == current_user or current_user in team.members):
            raise HTTPException(status_code=404, detail="Not found")

        return sk.TeamOut.from_orm(team)

    return router
