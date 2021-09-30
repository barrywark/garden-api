import fastapi
import oso
import app.models as models
import app.db as db
import app.api.ping as ping
import app.api.plants as plants
import app.api.users as users
import app.auth as auth

from app.settings import get_settings
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

_settings = get_settings()

# Oso setup
oso = oso.Oso()
oso.load_files(["app/policy.polar"])


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
app.include_router(plants.make_router(oso))
app.include_router(users.router)
app.include_router(auth.router)

@app.on_event("startup")
async def startup():
    models.create_all(db.ENGINE)