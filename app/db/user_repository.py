from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.user_models import User


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_google_sub(db: Session, google_sub: str):
    return db.query(User).filter(User.google_sub == google_sub).first()


def create_user(
    db: Session,
    email: str,
    full_name: str | None = None,
    auth_provider: str = "otp",
    google_sub: str | None = None,
):
    user = User(
        email=email,
        full_name=full_name,
        auth_provider=auth_provider,
        google_sub=google_sub,
        is_email_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update_last_login(db: Session, user: User):
    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)
    return user