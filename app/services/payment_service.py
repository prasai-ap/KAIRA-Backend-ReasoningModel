import uuid
import requests
from fastapi import HTTPException

from app.core.payment_config import (
    ESEWA_PRODUCT_CODE,
    ESEWA_SECRET_KEY,
    ESEWA_PAYMENT_URL,
    ESEWA_STATUS_CHECK_URL,
    ESEWA_SUCCESS_URL,
    ESEWA_FAILURE_URL,
    PACKAGE_NAME,
    PACKAGE_PRICE,
    PACKAGE_DURATION_DAYS,
)
from app.utils.esewa_utils import generate_esewa_signature
from app.db.payment_repository import (
    create_pending_payment,
    get_payment_by_transaction_uuid,
    mark_payment_success,
    mark_payment_failed,
    create_subscription,
    get_active_subscription,
    get_user_payments,
    get_subscription_by_payment_id,
    mark_invoice_sent,
)
from app.db.user_repository import get_user_by_id
from app.services.billing_email_service import send_invoice_email


def initiate_esewa_payment(db, user):
    transaction_uuid = f"KAIRA-{uuid.uuid4()}"

    payment = create_pending_payment(
        db=db,
        user_id=user.id,
        package_name=PACKAGE_NAME,
        amount=PACKAGE_PRICE,
        transaction_uuid=transaction_uuid,
    )

    signature = generate_esewa_signature(
        total_amount=PACKAGE_PRICE,
        transaction_uuid=transaction_uuid,
        product_code=ESEWA_PRODUCT_CODE,
        secret_key=ESEWA_SECRET_KEY,
    )

    form_data = {
        "amount": str(PACKAGE_PRICE),
        "tax_amount": "0",
        "total_amount": str(PACKAGE_PRICE),
        "transaction_uuid": transaction_uuid,
        "product_code": ESEWA_PRODUCT_CODE,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "success_url": ESEWA_SUCCESS_URL,
        "failure_url": ESEWA_FAILURE_URL,
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "signature": signature,
    }

    return {
        "payment_id": str(payment.id),
        "payment_method": "ESEWA",
        "payment_url": ESEWA_PAYMENT_URL,
        "form_data": form_data,
    }


def verify_esewa_payment(db, transaction_uuid, total_amount):
    if not transaction_uuid:
        raise HTTPException(status_code=400, detail="Transaction UUID missing")

    if not total_amount:
        raise HTTPException(status_code=400, detail="Total amount missing")

    payment = get_payment_by_transaction_uuid(db, transaction_uuid)

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    if payment.status == "SUCCESS":
        subscription = get_subscription_by_payment_id(db, payment.id)
        user = get_user_by_id(db, payment.user_id)

        if user and subscription and not payment.invoice_sent_at:
            try:
                send_invoice_email(user, payment, subscription)
                mark_invoice_sent(db, payment)
            except Exception as email_error:
                print(f"Invoice email failed: {email_error}")

        return {
            "message": "Payment already verified",
            "subscription_activated": True,
        }

    params = {
        "product_code": ESEWA_PRODUCT_CODE,
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
    }

    try:
        response = requests.get(
            ESEWA_STATUS_CHECK_URL,
            params=params,
            timeout=10,
        )
    except requests.RequestException:
        raise HTTPException(
            status_code=400,
            detail="Could not connect to eSewa verification service",
        )

    if response.status_code != 200:
        mark_payment_failed(db, payment)
        raise HTTPException(status_code=400, detail="Payment verification failed")

    data = response.json()
    status = data.get("status")

    if status == "COMPLETE":
        transaction_code = data.get("ref_id") or data.get("transaction_code")

        payment = mark_payment_success(
            db=db,
            payment=payment,
            transaction_code=transaction_code,
        )

        existing_subscription = get_subscription_by_payment_id(db, payment.id)

        if existing_subscription:
            subscription = existing_subscription
        else:
            subscription = create_subscription(
                db=db,
                user_id=payment.user_id,
                payment_id=payment.id,
                plan_name=PACKAGE_NAME,
                price=PACKAGE_PRICE,
                duration_days=PACKAGE_DURATION_DAYS,
            )

        user = get_user_by_id(db, payment.user_id)

        if user and not payment.invoice_sent_at:
            try:
                send_invoice_email(user, payment, subscription)
                mark_invoice_sent(db, payment)
            except Exception as email_error:
                print(f"Invoice email failed: {email_error}")

        return {
            "message": "Payment verified successfully",
            "subscription_activated": True,
        }

    mark_payment_failed(db, payment)
    raise HTTPException(status_code=400, detail="Payment not completed")


def get_my_subscription(db, user):
    subscription = get_active_subscription(db, user.id)

    if not subscription:
        return {
            "is_active": False,
            "plan_name": None,
            "end_date": None,
        }

    return {
        "is_active": True,
        "plan_name": subscription.plan_name,
        "end_date": subscription.end_date.isoformat(),
    }


def get_my_payment_history(db, user):
    payments = get_user_payments(db, user.id)

    return [
        {
            "id": str(p.id),
            "package_name": p.package_name,
            "amount": p.amount,
            "payment_method": p.payment_method,
            "status": p.status,
            "transaction_uuid": p.transaction_uuid,
            "transaction_code": p.transaction_code,
            "invoice_number": p.invoice_number,
            "invoice_sent_at": p.invoice_sent_at.isoformat() if p.invoice_sent_at else None,
            "created_at": p.created_at.isoformat(),
            "paid_at": p.paid_at.isoformat() if p.paid_at else None,
        }
        for p in payments
    ]