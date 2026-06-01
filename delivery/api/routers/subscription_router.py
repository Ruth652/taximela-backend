from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel

from infrastructure.db_dependency import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user as verify_token
from usecases.subscription_usecase import (
    initiate_subscription_usecase,
    handle_webhook_usecase,
    get_subscription_status_usecase,
    get_subscription_history_usecase,
)

router = APIRouter(prefix="/api/subscriptions", tags=["Subscriptions"])


class InitiateRequest(BaseModel):
    business_id: str


# ── Business owner endpoints ──────────────────────────────────────────────────

@router.post("/initiate")
async def initiate_subscription(
    body: InitiateRequest,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
):
    """
    Business owner initiates a featured listing subscription.
    Returns a Chapa checkout URL to redirect the user to payment.
    """
    return initiate_subscription_usecase(db, user["uid"], body.business_id)


@router.get("/status/{business_id}")
async def get_subscription_status(
    business_id: str,
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
):
    """
    Returns the current subscription status for a business.
    """
    return get_subscription_status_usecase(db, user["uid"], business_id)


@router.get("/history/{business_id}")
async def get_subscription_history(
    business_id: str,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    user: dict = Depends(verify_token),
):
    """
    Returns paginated subscription history for a business.
    """
    return get_subscription_history_usecase(db, user["uid"], business_id, page, limit)


# ── Chapa webhook (public — no auth) ─────────────────────────────────────────

@router.post("/webhook")
async def chapa_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Chapa calls this endpoint after payment success/failure.
    Verifies the payment and activates the subscription.
    """
    body = await request.json()
    tx_ref = body.get("tx_ref") or body.get("trx_ref")

    if not tx_ref:
        return {"message": "No tx_ref in webhook payload"}

    return handle_webhook_usecase(db, tx_ref)
