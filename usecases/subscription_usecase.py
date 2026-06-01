import os
import uuid
from fastapi import HTTPException
from sqlalchemy.orm import Session

from repository.subscription_repository import SubscriptionRepository
from repository.auth_identity_repository import AuthIdentityRepository
from repository.business_repository import BusinessRepository
from infrastructure.chapa_service import initialize_payment, verify_payment

SUBSCRIPTION_PRICE_ETB = float(os.getenv("FEATURED_SUBSCRIPTION_PRICE_ETB", "1000"))
SUBSCRIPTION_DURATION_DAYS = int(os.getenv("FEATURED_SUBSCRIPTION_DURATION_DAYS", "30"))
BACKEND_URL = os.getenv("BACKEND_URL", "https://taximela-backend-kxmi.onrender.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://taximela-business-owner.vercel.app")


def initiate_subscription_usecase(db: Session, firebase_uid: str, business_id: str) -> dict:
    """
    Initiates a Chapa payment for a featured listing subscription.
    Returns the Chapa checkout URL.
    """
    auth_repo = AuthIdentityRepository(db)
    business_repo = BusinessRepository(db)
    sub_repo = SubscriptionRepository(db)

    # Verify user exists
    user_id = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")

    # Verify business exists and belongs to this user
    business = business_repo.get_business_by_id(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if str(business.owner_id) != str(user_id):
        raise HTTPException(status_code=403, detail="You don't own this business")

    # Check if already has active subscription
    existing = sub_repo.get_active_by_business(business.id)
    if existing:
        raise HTTPException(
            status_code=400,
            detail=f"Business already has an active subscription until {existing.expires_at.strftime('%Y-%m-%d')}"
        )

    # Generate unique tx_ref — max 50 chars (Chapa limit)
    tx_ref = f"tm-{str(business_id).replace('-', '')[:16]}-{uuid.uuid4().hex[:8]}"

    # Get user info for Chapa
    from repository.user_repository import UserRepository
    user = UserRepository(db).get_user_by_id(user_id)
    name_parts = (user.full_name or "Business Owner").split(" ", 1)
    first_name = name_parts[0]
    last_name = name_parts[1] if len(name_parts) > 1 else ""

    # Initialize Chapa payment
    chapa_result = initialize_payment(
        tx_ref=tx_ref,
        amount=SUBSCRIPTION_PRICE_ETB,
        email=user.email,
        first_name=first_name,
        last_name=last_name,
        callback_url=f"{BACKEND_URL}/api/subscriptions/webhook",
        return_url=f"{FRONTEND_URL}/subscription/success?tx_ref={tx_ref}",
    )

    # Save pending subscription
    sub_repo.create_pending(
        business_id=business.id,
        amount_etb=SUBSCRIPTION_PRICE_ETB,
        tx_ref=tx_ref,
        checkout_url=chapa_result["checkout_url"],
    )

    return {
        "checkout_url": chapa_result["checkout_url"],
        "tx_ref": tx_ref,
        "amount_etb": SUBSCRIPTION_PRICE_ETB,
        "duration_days": SUBSCRIPTION_DURATION_DAYS,
    }


def handle_webhook_usecase(db: Session, tx_ref: str) -> dict:
    """
    Called by Chapa webhook. Verifies payment and activates subscription.
    """
    sub_repo = SubscriptionRepository(db)

    sub = sub_repo.get_by_tx_ref(tx_ref)
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")

    # Verify with Chapa
    try:
        chapa_data = verify_payment(tx_ref)
    except Exception as e:
        sub_repo.mark_failed(sub)
        raise HTTPException(status_code=400, detail=str(e))

    payment_status = chapa_data.get("data", {}).get("status", "")

    if payment_status == "success":
        sub_repo.activate(sub, duration_days=SUBSCRIPTION_DURATION_DAYS)
        return {"message": "Subscription activated"}
    else:
        sub_repo.mark_failed(sub)
        return {"message": f"Payment not successful: {payment_status}"}


def get_subscription_status_usecase(db: Session, firebase_uid: str, business_id: str) -> dict:
    auth_repo = AuthIdentityRepository(db)
    sub_repo = SubscriptionRepository(db)
    business_repo = BusinessRepository(db)

    user_id = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")

    business = business_repo.get_business_by_id(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if str(business.owner_id) != str(user_id):
        raise HTTPException(status_code=403, detail="You don't own this business")

    active = sub_repo.get_active_by_business(business.id)

    return {
        "is_featured": business.is_featured,
        "featured_until": business.featured_until.isoformat() if business.featured_until else None,
        "active_subscription": {
            "id": str(active.id),
            "status": active.status,
            "amount_etb": active.amount_etb,
            "started_at": active.started_at.isoformat() if active.started_at else None,
            "expires_at": active.expires_at.isoformat() if active.expires_at else None,
        } if active else None,
    }


def get_subscription_history_usecase(db: Session, firebase_uid: str, business_id: str, page: int, limit: int) -> dict:
    auth_repo = AuthIdentityRepository(db)
    sub_repo = SubscriptionRepository(db)
    business_repo = BusinessRepository(db)

    user_id = auth_repo.get_user_uuid_by_firebase_uid(firebase_uid)
    if not user_id:
        raise HTTPException(status_code=401, detail="User not found")

    business = business_repo.get_business_by_id(business_id)
    if not business:
        raise HTTPException(status_code=404, detail="Business not found")
    if str(business.owner_id) != str(user_id):
        raise HTTPException(status_code=403, detail="You don't own this business")

    result = sub_repo.get_history_by_business(business.id, page, limit)
    return {
        "data": [
            {
                "id": str(s.id),
                "status": s.status,
                "amount_etb": s.amount_etb,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "expires_at": s.expires_at.isoformat() if s.expires_at else None,
                "created_at": s.created_at.isoformat() if s.created_at else None,
            }
            for s in result["data"]
        ],
        "total": result["total"],
        "page": result["page"],
        "limit": result["limit"],
    }
