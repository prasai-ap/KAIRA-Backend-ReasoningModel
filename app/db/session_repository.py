from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session

from app.models.session_models import RefreshSession


def create_refresh_session(db: Session, **kwargs):
    session = RefreshSession(**kwargs)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_refresh_session_by_token_hash(db: Session, token_hash: str):
    return (
        db.query(RefreshSession)
        .filter(
            RefreshSession.refresh_token_hash == token_hash,
            RefreshSession.is_revoked == False,
        )
        .first()
    )


def revoke_refresh_session(db: Session, session: RefreshSession):
    session.is_revoked = True
    session.revoked_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session

def revoke_all_user_sessions(db: Session, user_id):
    sessions = (
        db.query(RefreshSession)
        .filter(
            RefreshSession.user_id == user_id,
            RefreshSession.is_revoked == False,
        )
        .all()
    )

    now = datetime.now(timezone.utc)
    for session in sessions:
        session.is_revoked = True
        session.revoked_at = now

    db.commit()
    return len(sessions)


def cleanup_revoked_sessions(db: Session):
    deleted_count = (
        db.query(RefreshSession)
        .filter(RefreshSession.is_revoked == True)
        .delete(synchronize_session=False)
    )

    db.commit()
    return deleted_count


def cleanup_expired_sessions(db: Session, days: int = 7):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    deleted_count = (
        db.query(RefreshSession)
        .filter(
            RefreshSession.expires_at < cutoff,
        )
        .delete(synchronize_session=False)
    )

    db.commit()
    return deleted_count
