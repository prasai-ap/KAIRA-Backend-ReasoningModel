import uuid

import stripe
from fastapi import HTTPException, Request

from app.core.stripe_config import (
    STRIPE_WEBHOOK_SECRET,
    STRIPE_CURRENCY,
    STRIPE_PACKAGE_AMOUNT_MINOR,
    STRIPE_SUCCESS_URL,
    STRIPE_CANCEL_URL,
    PACKAGE_NAME,
    PACKAGE_DURATION_DAYS,
)

from app.db.payment_repository import (
    create_pending_payment,
    update_payment_stripe_session,
    get_payment_by_stripe_session_id,
    mark_payment_paid,
    mark_payment_failed,
    activate_or_extend_subscription,
)


def create_stripe_checkout_session(db, user):
    payment = create_pending_payment(
        db=db,
        user_id=user.id,
        package_name=PACKAGE_NAME,
        amount=STRIPE_PACKAGE_AMOUNT_MINOR,
        currency=STRIPE_CURRENCY.upper(),
        payment_method="STRIPE",
        transaction_uuid=f"stripe_{uuid.uuid4().hex}",
    )

    try:
        checkout_session = stripe.checkout.Session.create(
            mode="payment",
            payment_method_types=["card"],
            customer_email=user.email,
            client_reference_id=str(user.id),
            line_items=[
                {
                    "price_data": {
                        "currency": STRIPE_CURRENCY,
                        "product_data": {
                            "name": PACKAGE_NAME,
                            "description": f"{PACKAGE_DURATION_DAYS} days premium access to KAIRA AI astrology interpretation",
                        },
                        "unit_amount": STRIPE_PACKAGE_AMOUNT_MINOR,
                    },
                    "quantity": 1,
                }
            ],
            metadata={
                "user_id": str(user.id),
                "payment_id": str(payment.id),
                "payment_method": "STRIPE",
                "package_name": PACKAGE_NAME,
                "duration_days": str(PACKAGE_DURATION_DAYS),
            },
            success_url=STRIPE_SUCCESS_URL,
            cancel_url=STRIPE_CANCEL_URL,
        )

        update_payment_stripe_session(
            db=db,
            payment=payment,
            session_id=checkout_session.id,
        )

        return {
            "payment_method": "STRIPE",
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
        }

    except Exception as error:
        mark_payment_failed(db, payment)

        raise HTTPException(
            status_code=500,
            detail=f"Stripe checkout session creation failed: {str(error)}",
        )


async def handle_stripe_webhook(request: Request, db):
    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=signature,
            secret=STRIPE_WEBHOOK_SECRET,
        )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Stripe payload")

    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid Stripe signature")

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]

        session_id = session.get("id")
        payment_status = session.get("payment_status")
        payment_intent_id = session.get("payment_intent")

        if payment_status == "paid":
            payment = get_payment_by_stripe_session_id(
                db=db,
                session_id=session_id,
            )

            if payment and payment.payment_status != "PAID":
                mark_payment_paid(
                    db=db,
                    payment=payment,
                    stripe_payment_intent_id=payment_intent_id,
                )

                activate_or_extend_subscription(
                    db=db,
                    user_id=payment.user_id,
                    plan_name=payment.package_name,
                    price=payment.amount,
                    duration_days=PACKAGE_DURATION_DAYS,
                    payment_id=payment.id,
                )

    return {"status": "success"}