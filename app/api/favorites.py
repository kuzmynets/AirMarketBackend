from fastapi import APIRouter, Depends
from firebase_admin import firestore
from app.core.auth import verify_token

router = APIRouter(prefix="/favorites", tags=["Favorites"])
db = firestore.client()

@router.get("/")
def get_favorites(user_data=Depends(verify_token)):
    user_id = user_data["uid"]
    favs_ref = db.collection("users").document(user_id).collection("favorites").stream()

    fav_ids = [doc.id for doc in favs_ref]
    if not fav_ids:
        return []

    ads = []
    for ad_id in fav_ids:
        ad_doc = db.collection("ads").document(ad_id).get()
        if ad_doc.exists:
            ad_data = ad_doc.to_dict()
            ads.append({
                "id": ad_doc.id,
                "title": ad_data.get("title"),
                "price": ad_data.get("price"),
                "images": ad_data.get("images", []),
                "created_at": ad_data.get("created_at")
            })
    return ads