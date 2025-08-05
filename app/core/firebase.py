import firebase_admin
from firebase_admin import credentials, auth, firestore

cred = credentials.Certificate("firebase-key.json")

try:
    firebase_admin.initialize_app(cred)
except Exception:
    pass

db = firestore.client()

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
