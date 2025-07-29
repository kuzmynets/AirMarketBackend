from app.core.firebase import db
from app.schemas.user import UserCreate
from app.core.security import hash_password

def get_user_by_email(email: str):
    query = db.collection("users").where("email", "==", email).limit(1).stream()
    for doc in query:
        user = doc.to_dict()
        user["id"] = doc.id
        return user
    return None

def create_user(user: UserCreate):
    data = {
        "email": user.email,
        "hashed_password": hash_password(user.password)
    }
    db.collection("users").add(data)
    return data