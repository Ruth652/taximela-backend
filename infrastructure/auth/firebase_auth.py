import firebase_admin
import os
from firebase_admin import auth, credentials
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Initialize Firebase app only once

FIREBASE_CREDENTIALS = os.getenv("FIREBASE_CREDENTIALS")
if not firebase_admin._apps:
    cred = credentials.Certificate(FIREBASE_CREDENTIALS)
    firebase_admin.initialize_app(cred)

security = HTTPBearer()

def get_current_firebase_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Verify Firebase token and return decoded token.
    Contains uid, email, and other claims.
    """
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
