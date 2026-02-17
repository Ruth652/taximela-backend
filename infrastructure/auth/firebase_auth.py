import os
import json
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")

if not FIREBASE_CREDENTIALS:
    raise ValueError("FIREBASE_CREDENTIALS environment variable not set")

if not firebase_admin._apps:
    cred_dict = json.loads(FIREBASE_CREDENTIALS)
    cred = credentials.Certificate(cred_dict)
    firebase_admin.initialize_app(cred)

security = HTTPBearer()

def get_current_firebase_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )