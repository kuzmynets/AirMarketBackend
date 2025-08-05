from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import get_user_by_token
from app.core.auth import get_token

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile")
def get_profile(token: str = Depends(get_token)):
    try:
        return get_user_by_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
