from sqlalchemy.orm import Session

from app.models.otp_models import OTPCode
from datetime import datetime, timezone


def create_otp_record(db: Session, **kwargs):
    otp_record = OTPCode(**kwargs)
    db.add(otp_record)
    db.commit()
    db.refresh(otp_record)
    return otp_record


def get_latest_otp(db: Session, email: str, purpose: str):
    return (
        db.query(OTPCode)
        .filter(OTPCode.email == email, OTPCode.purpose == purpose)
        .order_by(OTPCode.created_at.desc())
        .first()
    )


def mark_otp_used(db: Session, otp_record: OTPCode):
    otp_record.used = True
    db.commit()
    db.refresh(otp_record)
    return otp_record


def increment_attempt_count(db: Session, otp_record: OTPCode):
    otp_record.attempt_count += 1
    db.commit()
    db.refresh(otp_record)
    return otp_record


def delete_used_otps(db: Session):
    count = (
        db.query(OTPCode)
        .filter(OTPCode.used == True)
        .delete(synchronize_session=False)
    )
    db.commit()
    return count


def delete_expired_otps(db: Session):
    now = datetime.now(timezone.utc)

    count = (
        db.query(OTPCode)
        .filter(OTPCode.expires_at < now)
        .delete(synchronize_session=False)
    )
    db.commit()
    return count


def cleanup_otps(db: Session):
    used_count = delete_used_otps(db)
    expired_count = delete_expired_otps(db)

    return {
        "used_deleted": used_count,
        "expired_deleted": expired_count,
    }