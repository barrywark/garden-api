import fastapi

from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

import app.api.ping as ping
import app.api.plants as plants
import app.api.users as users

from app.settings import get_settings

_settings = get_settings()


# App setup
app = fastapi.FastAPI()

app.add_middleware(SessionMiddleware, secret_key=_settings.session_secret_key)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ping.router)
app.include_router(plants.make_router())
app.include_router(users.make_router())



# @app.on_event("startup")
# async def on_startup():
#     """
#     Startup event
#     """
#     # Not needed if you setup a migration system like Alembic
#     await db.create_db_and_tables()