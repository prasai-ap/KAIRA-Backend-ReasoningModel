from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.models.chat_models import ChatSession, ChatMessage


def create_session(db: Session, user_id, title: str):
    session = ChatSession(user_id=user_id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def get_session(db: Session, session_id, user_id):
    return (
        db.query(ChatSession)
        .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
        .first()
    )


def get_user_sessions(db: Session, user_id):
    return (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.updated_at.desc())
        .all()
    )


def add_message(db: Session, session_id, user_id, role, content):
    msg = ChatMessage(
        session_id=session_id,
        user_id=user_id,
        role=role,
        content=content,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def get_messages(db: Session, session_id, user_id):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.session_id == session_id, ChatMessage.user_id == user_id)
        .order_by(ChatMessage.created_at.asc())
        .all()
    )


def update_session_time(db: Session, session: ChatSession):
    session.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session


def update_session_title(db: Session, session: ChatSession, title: str):
    session.title = title
    session.updated_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session

def get_recent_messages(db: Session, session_id, user_id, days: int = 30, limit: int = 12):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)

    return (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id == session_id,
            ChatMessage.user_id == user_id,
            ChatMessage.created_at >= cutoff,
        )
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
        .all()[::-1]
    )