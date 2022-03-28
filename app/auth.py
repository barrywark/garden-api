from functools import reduce

import oso
import sqlmodel as sql

from fastapi import Depends
from polar.data.adapter.sqlalchemy_adapter import SqlAlchemyAdapter

import app.models as models
import app.db as db
from app.api.users import fastapi_users

current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)

_oso = oso.Oso()

_oso.register_class(models.User)
_oso.register_class(
    models.Species,
    fields={
        "owner": oso.Relation(
            kind="one", 
            other_type="User", 
            my_field="owner_id", 
            other_field="id")
    }
)

_oso.load_files(
    ("app/policy.polar",)
    )


def get_oso(session: db.Session = Depends(db.get_sync_session)) -> oso.Oso:
    _oso.set_data_filtering_adapter(SqlAlchemyAdapter(session))
    return _oso
