import uuid

import sqlalchemy.orm as orm
import app.models as m
import app.schemas as sk

def get_user_by_guid(db: orm.Session, user_guid: uuid.UUID) -> m.User:
    return db.query(m.User).filter(m.User.guid == user_guid).one_or_none()

def get_user_by_id(db: orm.Session, user_id: int) -> m.User:
    return db.query(m.User).filter(m.User.id == user_id).one_or_none()
