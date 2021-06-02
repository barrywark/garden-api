import fastapi

import app.models as models
import app.db as db
import app.api.ping as ping

# Database setup
models.create_all(db.ENGINE)

# App setup
app = fastapi.FastAPI()
app.include_router(ping.router)  