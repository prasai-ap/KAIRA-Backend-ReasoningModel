import sys
from pathlib import Path

BASEDIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASEDIR))


import uuid
from datetime import datetime, timezone, timedelta

from app.core.database import SessionLocal
from app.models.payment_models import PaymentTransaction, UserSubscription
from app.db.user_repository import get_user_by_id
from app.db.payment_repository import mark_invoice_sent
from app.services.billing_email_service import send_invoice_email


USER_ID = "caf86ab4-7f1b-47c0-9293-99ab75cfd813"

PACKAGE_NAME = "KAIRA Monthly Premium"
PACKAGE_PRICE = 500
PACKAGE_DURATION_DAYS = 30


db = SessionLocal()

try:
    user = get_user_by_id(db, USER_ID)

    if not user:
        raise Exception("User not found. Check USER_ID.")

    payment = PaymentTransaction(
        user_id=user.id,
        package_name=PACKAGE_NAME,
        amount=PACKAGE_PRICE,
        transaction_uuid=f"MANUAL-ESEWA-{uuid.uuid4()}",
        transaction_code="MANUAL-TEST",
        payment_method="ESEWA",
        status="SUCCESS",
        paid_at=datetime.now(timezone.utc),
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    start = datetime.now(timezone.utc)
    end = start + timedelta(days=PACKAGE_DURATION_DAYS)

    subscription = UserSubscription(
        user_id=user.id,
        payment_id=payment.id,
        plan_name=PACKAGE_NAME,
        price=PACKAGE_PRICE,
        start_date=start,
        end_date=end,
        is_active=True,
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    send_invoice_email(user, payment, subscription)
    mark_invoice_sent(db, payment)

    print("Manual eSewa payment activated successfully.")
    print("Invoice email sent successfully.")
    print("Payment ID:", payment.id)
    print("Transaction UUID:", payment.transaction_uuid)
    print("Subscription Ends:", subscription.end_date)

except Exception as error:
    db.rollback()
    print("Manual activation failed:", error)

finally:
    db.close()