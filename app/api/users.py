import fastapi
import app

router = fastapi.APIRouter()

@router.get("/me", response_model=app.models.User)
async def get_current_user(u: app.models.User = fastapi.Depends(app.auth.current_user)):
    return u