from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore
from datetime import datetime
from app.schemas.ad import CreateAd, UpdateAd
from app.core.auth import verify_token
import uuid

router = APIRouter(prefix="/ads", tags=["Ads"])
db = firestore.client()

# Створення оголошення
@router.post("/")
def create_ad(ad: CreateAd, user_data=Depends(verify_token)):
    ad_id = str(uuid.uuid4())

    # Отримуємо дані продавця з колекції users
    seller_ref = db.collection("users").document(user_data["uid"]).get()
    seller = seller_ref.to_dict() or {}

    ad_data = {
        "title": ad.title,
        "description": ad.description,
        "price": ad.price,
        "images": ad.images,
        "created_at": datetime.utcnow(),
        "user_id": user_data["uid"],
        "seller_name": seller.get("first_name", "Невідомий"),
        "seller_avatar": seller.get("avatar", "")
    }

    db.collection("ads").document(ad_id).set(ad_data)
    return {"id": ad_id, "message": "Ad created successfully"}

# Отримання всіх оголошень
@router.get("/")
def get_ads(user_data=Depends(verify_token)):
    ads = db.collection("ads").stream()

    # Отримуємо список вибраного користувача
    user_doc = db.collection("users").document(user_data["uid"]).get().to_dict() or {}
    favorites = user_doc.get("favorites", [])

    return [
        {
            **ad.to_dict(),
            "id": ad.id,
            "is_favorite": ad.id in favorites
        }
        for ad in ads
    ]

# Отримання своїх оголошень
@router.get("/my")
def get_my_ads(user_data=Depends(verify_token)):
    user_id = user_data["uid"]
    ads = db.collection("ads").where("user_id", "==", user_id).stream()
    return [{**ad.to_dict(), "id": ad.id} for ad in ads]

# Отримання конкретного оголошення з інфою про продавця
@router.get("/{ad_id}")
def get_ad(ad_id: str, user_data=Depends(verify_token)):
    ad_ref = db.collection("ads").document(ad_id)
    ad_doc = ad_ref.get()
    if not ad_doc.exists:
        raise HTTPException(status_code=404, detail="Ad not found")

    ad_data = ad_doc.to_dict()
    user_id = ad_data.get("user_id")

    # Отримуємо продавця
    seller = {}
    if user_id:
        seller_ref = db.collection("users").document(user_id).get()
        if seller_ref.exists:
            seller_data = seller_ref.to_dict()
            full_name_parts = [
                seller_data.get("first_name", ""),
                seller_data.get("second_name", ""),
                seller_data.get("last_name", "")
            ]
            full_name = " ".join(filter(None, full_name_parts))
            seller = {
                "name": full_name.strip() or "Невідомий",
                "avatar": seller_data.get("avatar", "")
            }

    # Перевіряємо, чи у вибраному
    is_favorite = False
    try:
        fav_doc = db.collection("users").document(user_data["uid"]).collection("favorites").document(ad_id).get()
        if fav_doc.exists:
            is_favorite = True
    except:
        pass

    return {
        "id": ad_doc.id,
        "title": ad_data.get("title"),
        "description": ad_data.get("description"),
        "price": ad_data.get("price"),
        "images": ad_data.get("images", []),
        "created_at": ad_data.get("created_at"),
        "seller": seller,
        "is_favorite": is_favorite
    }

# Додавання / видалення з вибраного
@router.post("/{ad_id}/favorite")
def toggle_favorite(ad_id: str, user_data=Depends(verify_token)):
    user_id = user_data["uid"]

    ad_ref = db.collection("ads").document(ad_id)
    if not ad_ref.get().exists:
        raise HTTPException(status_code=404, detail="Ad not found")

    fav_ref = db.collection("users").document(user_id).collection("favorites").document(ad_id)
    fav_doc = fav_ref.get()

    if fav_doc.exists:
        fav_ref.delete()
        return {"message": "Removed from favorites", "is_favorite": False}
    else:
        fav_ref.set({"added_at": firestore.SERVER_TIMESTAMP})
        return {"message": "Added to favorites", "is_favorite": True}

# Оновлення оголошення
@router.put("/{ad_id}")
def update_ad(ad_id: str, updated: UpdateAd, user_data=Depends(verify_token)):
    ad_ref = db.collection("ads").document(ad_id)
    ad = ad_ref.get()
    if not ad.exists:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.to_dict()["user_id"] != user_data["uid"]:
        raise HTTPException(status_code=403, detail="Not your ad")
    ad_ref.update({k: v for k, v in updated.dict().items() if v is not None})
    return {"message": "Ad updated"}

# Видалення оголошення
@router.delete("/{ad_id}")
def delete_ad(ad_id: str, user_data=Depends(verify_token)):
    ad_ref = db.collection("ads").document(ad_id)
    ad = ad_ref.get()
    if not ad.exists:
        raise HTTPException(status_code=404, detail="Ad not found")
    if ad.to_dict()["user_id"] != user_data["uid"]:
        raise HTTPException(status_code=403, detail="Not your ad")
    ad_ref.delete()
    return {"message": "Ad deleted"}