import fastapi
import oso
import app.models as models
import app.db as db
import app.api.ping as ping
import app.api.plants as plants

from app.settings import get_settings

_settings = get_settings()

# App setup
app = fastapi.FastAPI()
oso = oso.Oso()
oso.load_file("app/policy.polar")


app.include_router(ping.router)
app.include_router(plants.make_router(oso))


@app.on_event("startup")
async def startup():
    models.create_all(db.ENGINE)