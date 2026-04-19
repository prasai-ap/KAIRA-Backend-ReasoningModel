from fastapi import HTTPException

from app.db.chat_repository import (
    create_session,
    get_session,
    get_user_sessions,
    add_message,
    get_messages,
    update_session_time,
    update_session_title,
)
from app.db.user_astrology_repository import get_user_astrology
from app.services.ai_service import generate_ai_response


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

    history_text = ""
    if history:
        history_text = "\n".join(
            [f"{m.role.upper()}: {m.content}" for m in history[-10:]]
        )
    else:
        history_text = "No previous chat history. This is the first interaction."

    return f"""
You are an expert Vedic astrology AI assistant.

Instructions:
- The user's astrology data is authoritative and must always be used.
- Use prior conversation history when available.
- If no prior chat history exists, answer using the astrology data and current user message only.
- Do not invent astrology details that are not present in the stored data.
- Explain clearly in simple language.
- Be practical and user-friendly.

{astrology_text}

Conversation history:
{history_text}

Latest user message:
USER: {user_message}

ASSISTANT:
""".strip()


def send_message(db, user, message, session_id=None):
    astrology = get_user_astrology(db, user.id)
    if not astrology:
        raise HTTPException(
            status_code=400,
            detail="Astrology data not found for user. Please generate astrology data first."
        )

    if session_id:
        session = get_session(db, session_id, user.id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")
    else:
        session = create_session(db, user.id, message[:40])

    add_message(db, session.id, user.id, "user", message)

    history = get_messages(db, session.id, user.id)

    prompt = build_prompt(astrology, history[:-1], message)
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