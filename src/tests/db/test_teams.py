import pytest
import uuid

import app.models as models
import app.api.teams as teams
import sqlalchemy as sql
import sqlalchemy.orm as orm

from tests.util import client, session

from unittest.mock import sentinel

@pytest.fixture
def team(session) -> models.Team:
    with session.begin():
        team = models.Team(name='Test Team')
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
