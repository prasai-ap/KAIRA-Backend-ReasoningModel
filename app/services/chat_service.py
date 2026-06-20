from fastapi import HTTPException
from datetime import datetime, timezone

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
from app.services.chat_history_service import summarize_chat_history
from app.rag.retriever import retrieve_phaladeepika_context


def build_prompt(astrology, chat_summary, rag_context, user_message):
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

    if not chat_summary:
        chat_summary = "No recent chat summary available."

    if not rag_context:
        rag_context = "No relevant Phaladeepika reference context retrieved."

    return f"""
You are Kaira, an expert Vedic astrology AI assistant.

Response Format:

DIRECT ANSWER:
- Give the direct answer first.
- Keep it short, clear, and practical.
- Maximum 2–4 lines.
- Do not start with a long greeting.

EXPLANATION:
- Then explain the astrology reasoning in detail.
- Use charts, dasha, yoga, dosha, houses, planets, signs, and divisional charts only when relevant.
- Use the retrieved Phaladeepika context only when it supports the answer.
- Keep the explanation understandable for a normal user.

CONTINUE THE CONVERSATION:
- End with one specific follow-up question.
- The follow-up must be related to the user's latest question and chart context.
- Do not use generic lines like "Do you want to know more?"
- Examples:
  - "Would you like me to check this through your current dasha timing?"
  - "Should I also compare this with your D10 career chart?"
  - "Would you like me to explain how this affects relationships specifically?"
  - "Should I check the stronger period for this result in your upcoming dasha?"

Important Rules:
- Use the astrology data as authoritative.
- Use summarized recent conversation history only for context.
- Use retrieved Phaladeepika context only when relevant.
- Do not invent missing astrology details.
- Do not claim Phaladeepika says something unless it appears in the retrieved context.
- If data is insufficient, say clearly.
- Today's date is {today}.
- Always determine the CURRENT dasha based on today's date for all dasha cycles provided.
- Ignore past dasha periods that have already ended.
- Only focus on active dasha periods unless the user asks about past or future timing.
- You may use future dasha periods only if relevant to the user's question.
- Keep the tone warm, confident, and conversational.

{astrology_text}

Summarized recent chat history:
{chat_summary}

Retrieved Phaladeepika reference context:
{rag_context}

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

    chat_summary = summarize_chat_history(history)

    try:
        rag_context = retrieve_phaladeepika_context(message)
    except Exception:
        rag_context = "No relevant Phaladeepika reference context retrieved."

    prompt = build_prompt(
        astrology=astrology,
        chat_summary=chat_summary,
        rag_context=rag_context,
        user_message=message,
    )

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