import os
import json
import firebase_admin
from firebase_admin import auth, credentials, messaging
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# Load .env locally
load_dotenv()

# Prevent re-initializing Firebase
if not firebase_admin._apps:

    if os.getenv("ENV") == "production":
        firebase_credentials = os.getenv("FIREBASE_CREDENTIALS")

        if not firebase_credentials:
            raise ValueError("FIREBASE_CREDENTIALS environment variable not set")

        cred_dict = json.loads(firebase_credentials)
        cred = credentials.Certificate(cred_dict)

    else:
        cred = credentials.Certificate("firebase_key.json")

    firebase_admin.initialize_app(cred)
    print("Running in:", os.getenv("ENV", "development"))


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

def create_firebase_user(email: str, password: str, display_name: str = None, fcm_token: str = None):
    try:
        user = auth.create_user(
            email=email,
            password=password,
            display_name=display_name,
            fcm_token=fcm_token
        )
        return user
    
    except auth.EmailAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists in Firebase."
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Firebase error: {str(e)}"
        )
 

def set_firebase_custom_claims(firebase_uid: str, claims: dict) -> None:
    """
    Sets custom claims on a Firebase user (e.g. {"role": "operational_admin"}).
    These claims are embedded in the user's JWT on next token refresh.
    """
    try:
        auth.set_custom_user_claims(firebase_uid, claims)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set custom claims: {str(e)}"
        )

def send_push_notification(
    fcm_token: str,
    title: str,
    body: str
):
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=fcm_token
        )

        response = messaging.send(message)
        return response

    except Exception as e:
        print(f"Push notification failed: {e}")
        return None

def generate_password_reset_link(email: str) -> str:
    """
    Generates a Firebase password-reset link for the given email.
    Used to let a newly created admin set their own password.
    """
    try:
        return auth.generate_password_reset_link(email)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate password reset link: {str(e)}"
        )

 



 

