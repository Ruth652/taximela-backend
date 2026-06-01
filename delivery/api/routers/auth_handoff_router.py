from typing import Optional

from fastapi import APIRouter, Body, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from infrastructure.database import get_db
from infrastructure.auth.firebase_auth import get_current_firebase_user
from infrastructure.handoff_rate_limit import check_handoff_exchange_rate_limit
from usecases.auth_handoff_usecase import (
    HandoffError,
    mint_handoff_token,
    exchange_handoff_token,
)

router = APIRouter(prefix="/api/auth", tags=["Auth handoff"])


class MintHandoffRequest(BaseModel):
    purpose: Optional[str] = Field(
        default=None,
        description='Optional intent, e.g. "business_owner_web"',
    )


class MintHandoffResponse(BaseModel):
    handoff_token: str
    expires_in: int


class ExchangeHandoffRequest(BaseModel):
    handoff_token: str = Field(..., min_length=1)


class ExchangeHandoffResponse(BaseModel):
    custom_token: str
    owner_id: str


def _handoff_error_response(exc: HandoffError) -> JSONResponse:
    return JSONResponse(
        status_code=400,
        content={"message": exc.message, "code": exc.code},
    )


@router.post(
    "/handoff",
    response_model=MintHandoffResponse,
    status_code=201,
    summary="Mint one-time handoff token (mobile)",
    description=(
        "Authenticated mobile clients receive a short-lived token to open "
        "the owner web portal without signing in again."
    ),
)
def mint_handoff(
    body: MintHandoffRequest = Body(default_factory=MintHandoffRequest),
    firebase_user: dict = Depends(get_current_firebase_user),
    db: Session = Depends(get_db),
):
    purpose = body.purpose
    return mint_handoff_token(db, firebase_user["uid"], purpose=purpose)


@router.post(
    "/handoff/exchange",
    response_model=ExchangeHandoffResponse,
    summary="Exchange handoff token for Firebase custom token (web)",
    description=(
        "Public endpoint. Web apps redeem the one-time URL token and sign in "
        "via Firebase signInWithCustomToken."
    ),
    responses={
        400: {
            "description": "Invalid, expired, or already used handoff token",
            "content": {
                "application/json": {
                    "example": {
                        "message": "This link has expired.",
                        "code": "handoff_expired",
                    }
                }
            },
        },
        429: {"description": "Rate limit exceeded"},
    },
)
def exchange_handoff(
    body: ExchangeHandoffRequest,
    request: Request,
    db: Session = Depends(get_db),
):
    check_handoff_exchange_rate_limit(request)
    try:
        return exchange_handoff_token(db, body.handoff_token)
    except HandoffError as exc:
        return _handoff_error_response(exc)
