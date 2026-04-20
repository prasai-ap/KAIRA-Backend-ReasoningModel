from fastapi import HTTPException

from app.db.chat_repository import (
    create_session,
    get_session,
    get_user_sessions,
    add_message,
    get_messages,
    update_session_time,
    update_session_title,
    get_recent_messages,
    delete_session,
)
from app.db.user_astrology_repository import get_user_astrology
from app.services.ai_service import generate_ai_response
from datetime import datetime

def build_prompt(astrology, history, user_message):
    astrology_text = f"""
User Astrology Profile:
Charts:
{astrology.charts}

Dasha:
{astrology.dasha}

Yoga:
{astrology.yoga}

Dosha:
{astrology.dosha}
"""

    if history:
        history_text = "\n".join(
            [f"{m.role.upper()}: {m.content}" for m in history]
        )
    else:
        history_text = "No recent chat history in the last 30 days."

    return f"""
You are an expert Vedic astrology AI assistant.

Instructions:
- Use the astrology data as authoritative.
- Use recent conversation history if available.
- If no recent history exists, answer from astrology data and current user message.
- Do not invent missing astrology details.
- Answer clearly and practically.

IMPORTANT:
- Today's date is {today}
- ALWAYS determine the CURRENT dasha based on today's date for all the dasha cycles provided in the astrology data.
- Ignore past dasha periods that have already ended
- Only talk about the ACTIVE dasha period
-you may alos use future dasha periods if they are relevant to the user's question.

Rules:
- Use only provided astrology data
- Do NOT hallucinate or assume missing data
- If data is insufficient, say clearly

{astrology_text}

Recent conversation history (last 30 days only):
{history_text}

Latest user message:
USER: {user_message}

ASSISTANT:
""".strip()

def send_message(db, user, message, session_id=None):
    if session_id:
        session = get_session(db, session_id, user.id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        session = create_session(db, user.id, message[:40])

    add_message(db, session.id, user.id, "user", message)

    history = get_recent_messages(db, session.id, user.id, days=30, limit=12)
    astrology = get_user_astrology(db, user.id)

    prompt = build_prompt(astrology, history, message)
    reply = generate_ai_response(prompt)

    add_message(db, session.id, user.id, "assistant", reply)
    update_session_time(db, session)

    if not session.title or session.title == "New Chat":
        update_session_title(db, session, message[:40])

    return {
        "session_id": str(session.id),
        "reply": reply,
    }


def list_sessions(db, user):
    sessions = get_user_sessions(db, user.id)
    return [
        {
            "id": str(s.id),
            "title": s.title,
            "created_at": s.created_at.isoformat(),
            "updated_at": s.updated_at.isoformat(),
        }
        for s in sessions
    ]


def get_session_messages(db, user, session_id):
    session = get_session(db, session_id, user.id)
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    msgs = get_messages(db, session_id, user.id)
    return [
        {
            "id": str(m.id),
            "role": m.role,
            "content": m.content,
            "created_at": m.created_at.isoformat(),
        }
        for m in msgs
    ]

def delete_chat_session(db, user, session_id: str):
    session = get_session(db, session_id, user.id)

    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")

    delete_session(db, session)

    return {"message": "Chat deleted successfully"}