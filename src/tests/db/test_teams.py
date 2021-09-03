import pytest
import uuid

import app.models as models
import app.api.teams as teams
import sqlalchemy as sql
import sqlalchemy.orm as orm

from tests.util import session

from unittest.mock import sentinel

@pytest.fixture
def team(session) -> models.Team:
    with session.begin():
        owner = models.User(email='test@test.com', fullname='Foo Bar')
        team = models.Team(name='Test Team', owner=owner)
        session.add(team)

        return team


def test_get_by_guid(team: models.Team, session: orm.Session):
    assert teams.get_team_by_guid(session, team.guid).id == team.id

def test_get_by_id(team: models.Team, session: orm.Session):
    assert teams.get_team_by_id(session, team.id) is team

def test_create_adds_member(session: orm.Session):
    owner = models.User(email='test@test.com', fullname='Foo Bar')
    session.add(owner)

    team_name = "TEST NAME"
    team = teams.create_team(session, owner, team_name)

    assert team.id is not None
    assert team.name == team_name
    assert owner in team.members
    assert team.owner is owner

def test_adds_member(session: orm.Session, team: models.Team):
    member = models.User(email='member@test.com', fullname='Member')
    session.add(member)

    teams.add_member(session, team, member)

    assert member in team.members

def test_removes_member(session: orm.Session, team: models.Team):
    member = models.User(email='member@test.com', fullname='Member')
    session.add(member)

    teams.add_member(session, team, member)
    teams.remove_member(session, team, member)

    assert member not in team.members


def test_removing_non_member_raises(session: orm.Session, team: models.Team):
    member = models.User(email='member@test.com', fullname='Member')
    session.add(member)

    with pytest.raises(ValueError) as e:
        teams.remove_member(session, team, member)

def test_get_team_as_owner():
    assert False

def test_get_team_as_member():
    assert False

def test_get_team_requires_authorized_user():
    assert False

def test_get_team_404_if_not_member_or_owner():
    assert False