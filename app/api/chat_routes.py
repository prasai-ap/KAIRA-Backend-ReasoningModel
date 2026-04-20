from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.schemas.chat_schemas import SendMessageRequest
from app.services.chat_service import (
    send_message,
    list_sessions,
    get_session_messages,
    delete_chat_session,
)

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/message")
def chat(
    payload: SendMessageRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return send_message(db, user, payload.message, payload.session_id)


@router.get("/sessions")
def sessions(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return list_sessions(db, user)


@router.get("/sessions/{session_id}")
def messages(
    session_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return get_session_messages(db, user, session_id)

@router.delete("/sessions/{session_id}")
def delete_chat(
    session_id: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    return delete_chat_session(db, user, session_id)