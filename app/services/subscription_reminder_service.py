from app.core.database import SessionLocal
from app.db.payment_repository import (
    get_subscriptions_expiring_soon,
    mark_expiry_reminder_sent,
    get_expired_subscriptions_pending_email,
    mark_expired_email_sent,
)
from app.db.user_repository import get_user_by_id
from app.utils.email_utils import send_email
from app.utils.email_templates import (
    build_subscription_expiry_email_template,
    build_subscription_expired_email_template,
)


def send_expiry_reminders():
    db = SessionLocal()

    try:
        subscriptions = get_subscriptions_expiring_soon(db)

        for subscription in subscriptions:
            user = get_user_by_id(db, subscription.user_id)

            if not user:
                continue

            try:
                subject, html_body, text_body = build_subscription_expiry_email_template(
                    user=user,
                    subscription=subscription,
                )

                send_email(
                    to_email=user.email,
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body,
                )

                mark_expiry_reminder_sent(db, subscription)

            except Exception as email_error:
                print(f"Failed to send subscription expiry email: {email_error}")

    finally:
        db.close()

def send_expired_subscription_emails():
    db = SessionLocal()

    try:
        subscriptions = get_expired_subscriptions_pending_email(db)

        for subscription in subscriptions:
            user = get_user_by_id(db, subscription.user_id)

            if not user:
                continue

            try:
                subject, html_body, text_body = build_subscription_expired_email_template(
                    user=user,
                    subscription=subscription,
                )

                send_email(
                    to_email=user.email,
                    subject=subject,
                    html_body=html_body,
                    text_body=text_body,
                )

                mark_expired_email_sent(db, subscription)

            except Exception as email_error:
                print(f"Failed to send subscription expired email: {email_error}")

    finally:
        db.close()