from google.oauth2 import id_token
from google.auth.transport import requests

from app.core.auth_config import GOOGLE_CLIENT_ID


def verify_google_token(token: str):
    info = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID, clock_skew_in_seconds=10,)

    return {
        "email": info.get("email"),
        "full_name": info.get("name"),
        "google_sub": info.get("sub"),
        "profile_image_url": info.get("picture"),
        "email_verified": info.get("email_verified", False),
    }