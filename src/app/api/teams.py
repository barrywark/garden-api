import uuid

import sqlalchemy as sql
import sqlalchemy.orm as orm
import app.models as m
import app.schemas as sk

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