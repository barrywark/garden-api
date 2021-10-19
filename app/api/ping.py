from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/ping")
async def pong():
    return {"alive": True}
