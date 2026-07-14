import base64
import json

from fastapi import APIRouter, Depends, Request, HTTPException
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


router = APIRouter(prefix="/payment", tags=["payment"])


def decode_esewa_data(encoded_data: str):
    try:
        padding = "=" * (-len(encoded_data) % 4)
        decoded_bytes = base64.b64decode(encoded_data + padding)
        decoded_text = decoded_bytes.decode("utf-8")
        return json.loads(decoded_text)

    except Exception as error:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid eSewa data: {str(error)}",
        )


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
    data = request.query_params.get("data")

    transaction_uuid = request.query_params.get("transaction_uuid")
    total_amount = request.query_params.get("total_amount")

    if data:
        decoded_data = decode_esewa_data(data)

        print("ESEWA SUCCESS DECODED DATA:", decoded_data)

        transaction_uuid = decoded_data.get("transaction_uuid")
        total_amount = decoded_data.get("total_amount")
        esewa_status = decoded_data.get("status")

        if esewa_status != "COMPLETE":
            return RedirectResponse(
                url="http://localhost:5173/payment/failure?verified=false"
            )

    if not transaction_uuid or not total_amount:
        return RedirectResponse(
            url="http://localhost:5173/payment/failure?error=missing_payment_details"
        )

    total_amount = str(int(float(total_amount)))

    verify_esewa_payment(
        db=db,
        transaction_uuid=transaction_uuid,
        total_amount=total_amount,
    )

    return RedirectResponse(
        url=f"http://localhost:5173/payment/success?verified=true&transaction_uuid={transaction_uuid}"
    )


@router.get("/esewa/failure")
def esewa_failure(request: Request):
    print("ESEWA FAILURE QUERY PARAMS:", dict(request.query_params))

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