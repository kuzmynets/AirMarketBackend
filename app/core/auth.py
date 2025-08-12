from app.core.firebase import auth

from fastapi import Depends, Header, HTTPException
from fastapi.security import OAuth2PasswordBearer
from firebase_admin._auth_utils import InvalidIdTokenError


def get_token(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")
    return authorization.split(" ")[1]

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except InvalidIdTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")