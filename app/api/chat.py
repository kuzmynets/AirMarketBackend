from fastapi import APIRouter, Depends, HTTPException
from app.core.firebase import db
from pydantic import BaseModel
from app.core.auth import verify_token
import datetime

router = APIRouter(prefix="/chat", tags=["chat"])

# ---- Модель повідомлення ----
class Message(BaseModel):
    text: str

# ---- Отримання всіх чатів користувача ----
@router.get("/my_chats")
def get_my_chats(user_data=Depends(verify_token())):
    uid = user_data["uid"]
    chats_ref = db.collection("chats").where("participants", "array_contains", uid).stream()
    chat_list = []

    for chat_doc in chats_ref:
        chat_data = chat_doc.to_dict()

        participants = chat_data.get("participants", [])
        others = [u for u in participants if u != uid]
        other_uid = others[0] if others else None

        # Інфа про співрозмовника
        other_user_name = "Невідомий"
        other_user_avatar = None
        if other_uid:
            user_ref = db.collection("users").document(other_uid).get()
            if user_ref.exists:
                user_info = user_ref.to_dict()
                other_user_name = f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}".strip() or "Невідомий"
                other_user_avatar = user_info.get("avatar")

        # Останнє повідомлення
        last_msg_query = (
            db.collection("chats").document(chat_doc.id).collection("messages")
            .order_by("createdAt", direction="DESCENDING")
            .limit(1)
            .stream()
        )
        last_message, last_time = None, None
        for msg in last_msg_query:
            msg_data = msg.to_dict()
            last_message = msg_data.get("text")
            last_time = msg_data.get("createdAt")

        # ---- Підрахунок непрочитаних ----
        unread_count = 0
        msgs_ref = db.collection("chats").document(chat_doc.id).collection("messages").stream()
        for m in msgs_ref:
            msg_data = m.to_dict()
            if uid not in msg_data.get("readBy", []):
                unread_count += 1

        chat_list.append({
            "chat_id": chat_doc.id,
            "participants": participants,     # <<< тепер віддаємо всіх учасників
            "other_uid": other_uid,           # <<< залишаємо для зручності
            "other_user_name": other_user_name,
            "other_user_avatar": other_user_avatar,
            "last_message": last_message,
            "last_time": last_time,
            "unread_count": unread_count
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

    # Додаємо інфо про відправника
    user_ref = db.collection("users").document(user_data["uid"]).get()
    sender_name, sender_avatar = "Користувач", None
    if user_ref.exists:
        udata = user_ref.to_dict()
        sender_name = f"{udata.get('first_name', '')} {udata.get('last_name', '')}".strip() or "Користувач"
        sender_avatar = udata.get("avatar")

    chat_ref.collection("messages").document().set({
        "senderId": user_data["uid"],
        "senderName": sender_name,
        "senderAvatar": sender_avatar,
        "text": msg.text,
        "createdAt": datetime.datetime.utcnow(),
        "readBy": [user_data["uid"]]  # відправник автоматично прочитав
    })

    return {"status": "ok"}

# ---- Отримання повідомлень + помітка "прочитано" ----
@router.get("/{chat_id}/messages")
def get_messages(chat_id: str, user_data=Depends(verify_token())):
    uid = user_data["uid"]
    chat_ref = db.collection("chats").document(chat_id)
    if not chat_ref.get().exists:
        raise HTTPException(status_code=404, detail="Chat not found")

    messages_ref = chat_ref.collection("messages").order_by("createdAt").stream()
    messages = []

    for m in messages_ref:
        msg_data = m.to_dict()
        # Якщо користувач ще не відмічений як "прочитав" → додаємо його
        if uid not in msg_data.get("readBy", []):
            db.collection("chats").document(chat_id).collection("messages").document(m.id).update({
                "readBy": msg_data.get("readBy", []) + [uid]
            })
            msg_data["readBy"].append(uid)

        messages.append({"id": m.id, **msg_data})

    return messages