import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("firebase-key.json")
try:
    firebase_admin.initialize_app(cred)
except Exception as e:
    print(f"Firebase init error: {e}")
db = firestore.client()