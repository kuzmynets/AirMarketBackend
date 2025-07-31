from fastapi import APIRouter, Depends, HTTPException
from app.schemas.ad import AdCreate, AdUpdate, AdOut
from app.crud import ad as crud_ad
from app.api.auth import oauth2_scheme
from app.core.security import decode_token
from typing import List

router = APIRouter(prefix="/ads", tags=["ads"])

def get_current_user_email(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = decode_token(token)
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return email
    except:
        raise HTTPException(status_code=401, detail="Invalid token")

@router.post("/", response_model=AdOut)
def create_ad(ad: AdCreate, user_email: str = Depends(get_current_user_email)):
    created = crud_ad.create_ad(ad, user_email)
    return {**ad.dict(), "owner_email": user_email, "id": "N/A"}

@router.get("/", response_model=List[AdOut])
def list_ads():
    return crud_ad.get_all_ads()

@router.get("/{ad_id}", response_model=AdOut)
def get_ad(ad_id: str):
    ad = crud_ad.get_ad_by_id(ad_id)
    if not ad:
        raise HTTPException(status_code=404, detail="Ad not found")
    return ad

@router.put("/{ad_id}")
def update_ad(ad_id: str, update: AdUpdate, user_email: str = Depends(get_current_user_email)):
    result = crud_ad.update_ad(ad_id, update, user_email)
    if result is None:
        raise HTTPException(status_code=404, detail="Ad not found")
    if result == "unauthorized":
        raise HTTPException(status_code=403, detail="Not your ad")
    return {"detail": "Updated"}

@router.delete("/{ad_id}")
def delete_ad(ad_id: str, user_email: str = Depends(get_current_user_email)):
    result = crud_ad.delete_ad(ad_id, user_email)
    if result is None:
        raise HTTPException(status_code=404, detail="Ad not found")
    if result == "unauthorized":
        raise HTTPException(status_code=403, detail="Not your ad")
    return {"detail": "Deleted"}