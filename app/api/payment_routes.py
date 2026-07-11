from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.services.payment_service import (
    initiate_esewa_payment,
    verify_esewa_payment,
    get_my_subscription,
    get_my_payment_history,
)
from app.services.stripe_payment_service import (
    create_stripe_checkout_session,
    handle_stripe_webhook,
)

router = APIRouter(prefix="/payment", tags=["payment"])


@router.post("/esewa/initiate")
def initiate_payment(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return initiate_esewa_payment(db, user)


@router.get("/esewa/success")
def esewa_success(
    request: Request,
    db: Session = Depends(get_db),
):
    transaction_uuid = request.query_params.get("transaction_uuid")
    total_amount = request.query_params.get("total_amount")

    verify_esewa_payment(db, transaction_uuid, total_amount)

    return RedirectResponse(
        url="http://localhost:5173/payment/success"
    )


@router.get("/esewa/failure")
def esewa_failure():
    return RedirectResponse(
        url="http://localhost:5173/payment/failure"
    )


@router.get("/subscription")
def subscription(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return get_my_subscription(db, user)


@router.get("/history")
def payment_history(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return get_my_payment_history(db, user)


@router.post("/stripe/create-checkout-session")
def stripe_create_checkout_session(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_stripe_checkout_session(
        db=db,
        user=current_user,
    )


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    return await handle_stripe_webhook(
        request=request,
        db=db,
    )