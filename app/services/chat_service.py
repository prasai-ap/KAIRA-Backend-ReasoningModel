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
from datetime import datetime, timezone

def build_prompt(astrology, history, user_message):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

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

Response Format:
DIRECT ANSWER:
- Give the direct answer first.
- Keep it short, clear, and practical.
- Maximum 2–4 lines.

EXPLANATION:
- Then explain the astrology reasoning in detail.
- Use charts, dasha, yoga, and dosha only when relevant.
- Keep the explanation understandable.

Important Rules:
- Use the astrology data as authoritative.
- Use recent conversation history if available.
- If no recent history exists, answer from astrology data and current user message.
- Do not invent missing astrology details.
- If data is insufficient, say clearly.
- Today's date is {today}.
- Always determine the CURRENT dasha based on today's date for all dasha cycles provided.
- Ignore past dasha periods that have already ended.
- Only focus on active dasha periods unless the user asks about past or future timing.
- You may use future dasha periods only if relevant to the user's question.

{astrology_text}

Recent conversation history:
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
            detail="Astrology data not found for user. Please generate astrology data first.",
        )

    if session_id:
        session = get_session(db, session_id, user.id)
        if not session:
            raise HTTPException(status_code=404, detail="Chat session not found")

        history = get_recent_messages(db, session.id, user.id, days=30, limit=12)
    else:
        session = None
        history = []

    prompt = build_prompt(astrology, history, message)

    try:
        reply = generate_ai_response(prompt)
    except Exception:
        reply = "Sorry, I could not generate a response right now. Please try again."

    if session is None:
        session = create_session(db, user.id, message[:40])

    add_message(db, session.id, user.id, "user", message)
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