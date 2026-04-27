import smtplib
from email.message import EmailMessage
import os


EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


def send_email(to_email: str, subject: str, body: str):
    msg = EmailMessage()
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(EMAIL_HOST, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)


def send_register_otp_email(email: str, otp: str, full_name: str):
    subject = "Welcome to Kaira - Verify Your Email"

    body = f"""
Hi {full_name},

Welcome to Kaira!

Your registration OTP is:

{otp}

This OTP will expire soon. Please do not share it with anyone.

Thank you,
Kaira Team
"""

    send_email(email, subject, body)


def send_login_otp_email(email: str, otp: str):
    subject = "Your Kaira Login OTP"

    body = f"""
Hi,

Your login OTP is:

{otp}

This OTP will expire soon. Please do not share it with anyone.

Thank you,
Kaira Team
"""

    send_email(email, subject, body)