from sqlalchemy.orm import Session

from app.models.otp_models import OTPCode


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