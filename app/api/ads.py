from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import db, get_user_by_token
from app.core.auth import get_token
from pydantic import BaseModel
from typing import List
from datetime import datetime
import uuid

router = APIRouter(prefix="/ads", tags=["ads"])

class AdCreate(BaseModel):
    title: str
    description: str
    price: float

@router.post("/")
def create_ad(ad: AdCreate, token: str = Depends(get_token)):
    user = get_user_by_token(token)
    ad_id = str(uuid.uuid4())
    data = {
        "id": ad_id,
        "title": ad.title,
        "description": ad.description,
        "price": ad.price,
        "user_id": user["uid"],
        "created_at": datetime.utcnow().isoformat()
    }
    db.collection("ads").document(ad_id).set(data)
    return data

@router.get("/my")
def get_my_ads(token: str = Depends(get_token)):
    user = get_user_by_token(token)
    ads_ref = db.collection("ads").where("user_id", "==", user["uid"])
    docs = ads_ref.stream()
    return [doc.to_dict() for doc in docs]

@router.get("/{ad_id}")
def get_ad_detail(ad_id: str):
    doc = db.collection("ads").document(ad_id).get()
    if not doc.exists:
        raise HTTPException(status_code=404, detail="Ad not found")
    return doc.to_dict()

@router.delete("/{ad_id}")
def delete_ad(ad_id: str, token: str = Depends(get_token)):
    user = get_user_by_token(token)
    doc_ref = db.collection("ads").document(ad_id)
    doc = doc_ref.get()
    if not doc.exists or doc.to_dict().get("user_id") != user["uid"]:
        raise HTTPException(status_code=403, detail="Not allowed")
    doc_ref.delete()
    return {"detail": "Deleted"}