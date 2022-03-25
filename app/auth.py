from functools import reduce

import oso

from fastapi import Depends
from polar.data_filtering import Relation as polar_Relation
from polar.data.adapter.sqlalchemy_adapter import SqlAlchemyAdapter

import app.models as models
import app.db as db
from app.api.users import fastapi_users

current_user = fastapi_users.current_user()
current_active_user = fastapi_users.current_user(active=True)

_oso = oso.Oso()

# TODO add `build_query`
_oso.register_class(models.User)
_oso.register_class(models.Species)

_oso.load_files(
    ("app/policy.polar",)
    )

class AsyncSqlAlchemyAdapter(SqlAlchemyAdapter):
    def build_query(self, filter):
        types = filter.types

        def re(q, rel):
            typ = types[rel.left]
            rec = typ.fields[rel.name]
            left = typ.cls
            right = types[rec.other_type].cls
            return q.join(
                right, getattr(left, rec.my_field) == getattr(right, rec.other_field)
            )

        
        query = reduce(re, filter.relations, self.session.query(filter.model))
        disj = reduce(
            lambda a, b: a | b,
            [
                reduce(
                    lambda a, b: a & b,
                    [SqlAlchemyAdapter.sqlize(conj) for conj in conjs],
                    true(),
                )
                for conjs in filter.conditions
            ],
            false(),
        )
        return query.filter(disj).distinct()

def get_oso(session: db.Session = Depends(db.get_async_session)) -> oso.Oso:
    _oso.set_data_filtering_adapter(AsyncSqlAlchemyAdapter(session))
    return _oso

