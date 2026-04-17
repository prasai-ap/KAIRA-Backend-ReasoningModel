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
    db.commit()
    db.refresh(session)
    return session