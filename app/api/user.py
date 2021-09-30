import fastapi

import app.db
import app.models as m
import app.auth as auth



router = fastapi.APIRouter()

@router.get("/me", response_model=m.User)
async def get_current_user(u: m.User = fastapi.Depends(auth.current_user)):
    return u