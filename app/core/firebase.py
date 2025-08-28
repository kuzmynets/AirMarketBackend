import firebase_admin
from firebase_admin import credentials, auth as fb_auth, firestore

# 🔹 Ініціалізація Firebase один раз
cred = credentials.Certificate("firebase-key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)

db = firestore.client()
auth = fb_auth

# 🔹 Отримати користувача по токену
def get_user_by_token(token: str):
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        user = auth.get_user(uid)
        return {
            "uid": user.uid,
            "email": user.email,
            "name": user.display_name or ""
        }
    except Exception:
        raise Exception("Invalid Firebase token")