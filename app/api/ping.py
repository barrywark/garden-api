from fastapi import APIRouter, Depends

import app.auth as auth
import app.models as m

router = APIRouter()

@router.get("/ping")
async def pong():
    return {"alive": True}


@router.get("/authping")
async def authping(user: m.User = Depends(auth.current_user)):
    return {"authenticated": True}