from fastapi import APIRouter, Depends, HTTPException
from firebase_admin import firestore
from datetime import datetime
from app.core.auth import admin_required

router = APIRouter(prefix="/admin", tags=["Admin"])
db = firestore.client()

# ======================
# 🔹 Отримати всі оголошення, які очікують підтвердження
# ======================
@router.get("/pending_ads")
def get_pending_ads(user_data=Depends(admin_required)):
    ads = db.collection("ads").where("status", "==", "pending").stream()
    return [{**ad.to_dict(), "id": ad.id} for ad in ads]


# ======================
# 🔹 Зміна статусу оголошення (approve/reject)
# ======================
@router.post("/ads/{ad_id}/{action}")
def review_ad(ad_id: str, action: str, user_data=Depends(admin_required)):
    ad_ref = db.collection("ads").document(ad_id)
    ad_doc = ad_ref.get()
    if not ad_doc.exists:
        raise HTTPException(status_code=404, detail="Ad not found")

    if action not in ["approve", "reject"]:
        raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")

    new_status = "approved" if action == "approve" else "rejected"
    ad_ref.update({
        "status": new_status,
        "reviewed_at": datetime.utcnow(),
        "reviewed_by": user_data["uid"],
    })

    return {
        "message": f"Ad {new_status}",
        "ad_id": ad_id,
        "status": new_status
    }