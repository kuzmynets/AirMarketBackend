from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import get_user_by_token, db
from app.core.auth import  verify_token, optional_verify_token, get_current_user

router = APIRouter(prefix="/user", tags=["user"])

@router.get("/profile")
def get_profile(token: str = Depends(verify_token)):
    try:
        return get_user_by_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

@router.get("/me")
def get_me(user_data=Depends(get_current_user)):
    """
    Повертає інформацію про поточного користувача (uid, email, роль)
    """
    user_ref = db.collection("users").document(user_data["uid"]).get()
    user_info = user_ref.to_dict()

    return {
        "uid": user_data["uid"],
        "email": user_data.get("email"),
        "role": user_info.get("role", "user"),
    }
