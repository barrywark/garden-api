import fastapi

import app.models as models
import app.db as db
import app.api.ping as ping


# App setup
app = fastapi.FastAPI()
app.include_router(ping.router)  

@app.on_event("startup")
async def startup():
    models.create_all(db.ENGINE)