from app.core.firebase import db
from app.schemas.ad import AdCreate, AdUpdate

def create_ad(ad: AdCreate, owner_email: str):
    data = ad.dict()
    data["owner_email"] = owner_email
    ref = db.collection("ads").add(data)
    return data

def get_all_ads():
    ads_ref = db.collection("ads").stream()
    return [{"id": doc.id, **doc.to_dict()} for doc in ads_ref]

def get_ad_by_id(ad_id: str):
    doc = db.collection("ads").document(ad_id).get()
    if doc.exists:
        return {"id": doc.id, **doc.to_dict()}
    return None

def update_ad(ad_id: str, update_data: AdUpdate, requester_email: str):
    doc_ref = db.collection("ads").document(ad_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    ad = doc.to_dict()
    if ad["owner_email"] != requester_email:
        return "unauthorized"
    doc_ref.update({k: v for k, v in update_data.dict().items() if v is not None})
    return True

def delete_ad(ad_id: str, requester_email: str):
    doc_ref = db.collection("ads").document(ad_id)
    doc = doc_ref.get()
    if not doc.exists:
        return None
    ad = doc.to_dict()
    if ad["owner_email"] != requester_email:
        return "unauthorized"
    doc_ref.delete()
    return True
