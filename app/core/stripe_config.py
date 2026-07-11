import os
import stripe
from dotenv import load_dotenv

load_dotenv()

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET")

STRIPE_CURRENCY = os.getenv("STRIPE_CURRENCY").lower()
STRIPE_PACKAGE_AMOUNT_MINOR = int(os.getenv("STRIPE_PACKAGE_AMOUNT_MINOR"))

PACKAGE_NAME = os.getenv("PACKAGE_NAME")
PACKAGE_DURATION_DAYS = int(os.getenv("PACKAGE_DURATION_DAYS"))

STRIPE_SUCCESS_URL = os.getenv(
    "STRIPE_SUCCESS_URL",
    "http://localhost:5173/payment/success?session_id={CHECKOUT_SESSION_ID}",
)

STRIPE_CANCEL_URL = os.getenv(
    "STRIPE_CANCEL_URL",
    "http://localhost:5173/payment/cancel",
)


if STRIPE_SECRET_KEY:
    stripe.api_key = STRIPE_SECRET_KEY