from app.utils.email_utils import send_email
from app.utils.email_templates import build_invoice_email_template


def send_invoice_email(user, payment, subscription):
    subject, html_body, text_body = build_invoice_email_template(
        user=user,
        payment=payment,
        subscription=subscription,
    )

    send_email(
        to_email=user.email,
        subject=subject,
        html_body=html_body,
        text_body=text_body,
    )