from app.core.firebase import auth

from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
from firebase_admin._auth_utils import InvalidIdTokenError
from typing import Optional
from firebase_admin import auth as fb_auth

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# 🔹 Використовуємо для захищених роутів (токен обов'язковий)
def verify_token(optional: bool = False):
    async def _verify(authorization: Optional[str] = Header(None)):
        if not authorization:
            if optional:
                return None
            raise HTTPException(status_code=401, detail="Missing Authorization header")
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Invalid Authorization header")
        token = authorization.split(" ", 1)[1]
        try:
            decoded = fb_auth.verify_id_token(token)
            return {"uid": decoded["uid"], "email": decoded.get("email")}
        except Exception:
            if optional:
                return None
            raise HTTPException(status_code=401, detail="Invalid token")
    return _verify


# 🔹 Використовуємо для публічних роутів (токен може бути, а може й ні)
def optional_verify_token(authorization: Optional[str] = Header(None)):
    if not authorization:
        return None
    if not authorization.startswith("Bearer "):
        return None
    try:
        token = authorization.split(" ")[1]
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception:
        return None