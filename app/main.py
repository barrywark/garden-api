import fastapi

import app.models as models
import app.db as db
import app.api.ping as ping
import app.api.teams as teams
import app.schemas as sk

from fastapi_users import FastAPIUsers
from httpx_oauth.clients.google import GoogleOAuth2

from app.settings import get_settings

_settings = get_settings()


google_oauth_client = GoogleOAuth2(_settings.google_client_id,
                                    _settings.google_client_secret)

# def on_after_register(user: UserDB, request: Request):
#     print(f"User {user.id} has registered.")

_auth_backends = []

# App setup
app = fastapi.FastAPI()


_users = FastAPIUsers(db.get_db(), _auth_backends, sk.User, sk.UserCreate, sk.UserUpdate, models.User)

# google_oauth_router = fastapi_users.get_oauth_router(google_oauth_client, SECRET, after_register=on_after_register)
# app.include_router(google_oauth_router, prefix="/auth/google", tags=["auth"])

app.include_router(ping.router)
app.include_router(teams.make_router(_users))


@app.on_event("startup")
async def startup():
    models.create_all(db.ENGINE)