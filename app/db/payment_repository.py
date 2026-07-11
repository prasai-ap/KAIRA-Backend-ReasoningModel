import uuid
from datetime import datetime, timezone, timedelta

from app.models.payment_models import PaymentTransaction, UserSubscription


def create_pending_payment(
    db,
    user_id,
    package_name,
    amount,
    transaction_uuid=None,
    payment_method="ESEWA",
    currency="NPR",
):
    payment = PaymentTransaction(
        user_id=user_id,
        package_name=package_name,
        amount=amount,
        currency=currency,
        transaction_uuid=transaction_uuid or str(uuid.uuid4()),
        payment_method=payment_method.upper(),
        payment_status="PENDING",
    )

    db.add(payment)
    db.commit()
    db.refresh(payment)

    return payment


def get_payment_by_transaction_uuid(db, transaction_uuid):
    return (
        db.query(PaymentTransaction)
        .filter(PaymentTransaction.transaction_uuid == transaction_uuid)
        .first()
    )


def get_payment_by_stripe_session_id(db, session_id):
    return (
        db.query(PaymentTransaction)
        .filter(PaymentTransaction.stripe_checkout_session_id == session_id)
        .first()
    )


def get_user_payments(db, user_id):
    return (
        db.query(PaymentTransaction)
        .filter(PaymentTransaction.user_id == user_id)
        .order_by(PaymentTransaction.created_at.desc())
        .all()
    )



def update_payment_stripe_session(db, payment, session_id):
    payment.stripe_checkout_session_id = session_id
    payment.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(payment)

    return payment



def mark_payment_paid(
    db,
    payment,
    transaction_code=None,
    stripe_payment_intent_id=None,
):
    payment.payment_status = "PAID"
    payment.paid_at = datetime.now(timezone.utc)
    payment.updated_at = datetime.now(timezone.utc)

    if transaction_code:
        payment.transaction_code = transaction_code

    if stripe_payment_intent_id:
        payment.stripe_payment_intent_id = stripe_payment_intent_id

    db.commit()
    db.refresh(payment)

    return payment


def mark_payment_success(db, payment, transaction_code=None):
    return mark_payment_paid(
        db=db,
        payment=payment,
        transaction_code=transaction_code,
    )


def mark_payment_failed(db, payment):
    payment.payment_status = "FAILED"
    payment.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(payment)

    return payment


def mark_payment_cancelled(db, payment):
    payment.payment_status = "CANCELLED"
    payment.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(payment)

    return payment


def create_subscription(db, user_id, payment_id, plan_name, price, duration_days):
    start = datetime.now(timezone.utc)
    end = start + timedelta(days=duration_days)

    subscription = UserSubscription(
        user_id=user_id,
        payment_id=payment_id,
        plan_name=plan_name,
        price=price,
        start_date=start,
        end_date=end,
        is_active=True,
    )

    db.add(subscription)
    db.commit()
    db.refresh(subscription)

    return subscription


def get_active_subscription(db, user_id):
    now = datetime.now(timezone.utc)

    return (
        db.query(UserSubscription)
        .filter(
            UserSubscription.user_id == user_id,
            UserSubscription.is_active == True,
            UserSubscription.end_date > now,
        )
        .order_by(UserSubscription.end_date.desc())
        .first()
    )


def activate_or_extend_subscription(
    db,
    user_id,
    payment_id,
    plan_name,
    price,
    duration_days,
):
    now = datetime.now(timezone.utc)

    active_subscription = get_active_subscription(db, user_id)

    if active_subscription:
        active_subscription.end_date = active_subscription.end_date + timedelta(days=duration_days)
        active_subscription.payment_id = payment_id
        active_subscription.plan_name = plan_name
        active_subscription.price = price
        active_subscription.is_active = True

        db.commit()
        db.refresh(active_subscription)

        return active_subscription

    return create_subscription(
        db=db,
        user_id=user_id,
        payment_id=payment_id,
        plan_name=plan_name,
        price=price,
        duration_days=duration_days,
    )


def get_subscription_by_payment_id(db, payment_id):
    return (
        db.query(UserSubscription)
        .filter(UserSubscription.payment_id == payment_id)
        .first()
    )


def mark_invoice_sent(db, payment):
    if not payment.invoice_number:
        payment.invoice_number = f"INV-{payment.transaction_uuid}"

    payment.invoice_sent_at = datetime.now(timezone.utc)
    payment.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(payment)

    return payment


def get_subscriptions_expiring_soon(db):
    now = datetime.now(timezone.utc)
    next_24_hours = now + timedelta(days=1)

    return (
        db.query(UserSubscription)
        .filter(
            UserSubscription.is_active == True,
            UserSubscription.end_date > now,
            UserSubscription.end_date <= next_24_hours,
            UserSubscription.expiry_reminder_sent_at == None,
        )
        .all()
    )


def mark_expiry_reminder_sent(db, subscription):
    subscription.expiry_reminder_sent_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(subscription)

    return subscription


def get_expired_subscriptions_pending_email(db):
    now = datetime.now(timezone.utc)

    return (
        db.query(UserSubscription)
        .filter(
            UserSubscription.end_date <= now,
            UserSubscription.expired_email_sent_at == None,
        )
        .all()
    )


def mark_expired_email_sent(db, subscription):
    subscription.expired_email_sent_at = datetime.now(timezone.utc)
    subscription.is_active = False

    db.commit()
    db.refresh(subscription)

    return subscription