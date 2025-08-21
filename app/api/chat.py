from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import db
from pydantic import BaseModel
from app.core.auth import verify_token
import datetime

router = APIRouter(prefix="/chat", tags=["chat"])

# ---- Модель повідомлення ----
class Message(BaseModel):
    text: str

@router.get("/my_chats")
def get_my_chats(user_data=Depends(verify_token())):
    uid = user_data["uid"]
    chats_ref = db.collection("chats").where("participants", "array_contains", uid).stream()
    chat_list = []

    for chat_doc in chats_ref:
        chat_data = chat_doc.to_dict()
        other_uid = [u for u in chat_data["participants"] if u != uid][0]
        # Отримуємо дані співрозмовника
        user_ref = db.collection("users").document(other_uid).get()
        other_user_name = "Невідомий"
        if user_ref.exists:
            user_info = user_ref.to_dict()
            other_user_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip() or "Невідомий"
        chat_list.append({
            "chat_id": chat_doc.id,
            "other_uid": other_uid,
            "other_user_name": other_user_name
        })
    return chat_list

# ---- Створення або отримання чату ----
@router.post("/{other_uid}")
def create_chat(other_uid: str, user_data=Depends(verify_token())):
    uid = user_data["uid"]
    chat_id = "_".join(sorted([uid, other_uid]))
    chat_ref = db.collection("chats").document(chat_id)

    if not chat_ref.get().exists:
        chat_ref.set({
            "participants": [uid, other_uid],
            "createdAt": datetime.datetime.utcnow()
        })
    return {"chat_id": chat_id}

# ---- Відправка повідомлення ----
@router.post("/{chat_id}/send")
def send_message(chat_id: str, msg: Message, user_data=Depends(verify_token())):
    chat_ref = db.collection("chats").document(chat_id)
    if not chat_ref.get().exists:
        raise HTTPException(status_code=404, detail="Chat not found")

    chat_ref.collection("messages").document().set({
        "senderId": user_data["uid"],
        "text": msg.text,
        "createdAt": datetime.datetime.utcnow()
    })
    return {"status": "ok"}

# ---- Отримання повідомлень ----
@router.get("/{chat_id}/messages")
def get_messages(chat_id: str, user_data=Depends(verify_token())):
    chat_ref = db.collection("chats").document(chat_id)
    if not chat_ref.get().exists:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages = chat_ref.collection("messages").order_by("createdAt").stream()
    return [{"id": m.id, **m.to_dict()} for m in messages]

