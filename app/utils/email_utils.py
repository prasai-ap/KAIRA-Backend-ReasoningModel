import smtplib
from email.message import EmailMessage
import os

from app.utils.email_templates import build_otp_email_html

EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(to_email: str, subject: str, html_body: str):
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.set_content("Please view this email in an HTML-supported email client.")
    msg.add_alternative(html_body, subtype="html")

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)


def send_register_otp_email(email: str, otp: str, full_name: str):
    subject = "Welcome to Kaira - Verify Your Email"

    body = build_otp_email_html(
        full_name=full_name,
        otp=otp,
        title="Verify Your Email",
        subtitle="Welcome to Kaira. Use the OTP below to verify your email and begin exploring your astrology profile.",
    )

    send_email(email, subject, body)


def send_login_otp_email(email: str, otp: str, full_name: str):
    subject = "Your Kaira Login OTP"

    body = build_otp_email_html(
        full_name=full_name,
        otp=otp,
        title="Login Verification",
        subtitle="Use the OTP below to securely login to your Kaira account.",
    )

    send_email(email, subject, body)