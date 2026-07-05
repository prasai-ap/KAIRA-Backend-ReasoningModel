from fastapi import HTTPException
from datetime import datetime, timezone

from app.api.payment_routes import subscription
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
from app.db.payment_repository import get_active_subscription
from app.db.user_repository import increment_free_chat_used

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

Your main goal is to explain astrology in a way that a normal user can understand.
The user may not know astrology terms, so teach while answering.

RESPONSE FORMAT:

DIRECT ANSWER:
- Answer the user's question first in 2–4 short sentences.
- Use simple, practical language.
- Do not start with technical astrology terms.
- Be confident, but do not present astrology as absolute certainty.
- Use phrases like "this suggests", "this may indicate", or "this often shows" when appropriate.

EXPLANATION:
- Explain why you reached the answer.
- Always follow this order:
  1. What I found in your birth chart
  2. What it means in simple language
  3. How it may affect your real life
  4. Why this conclusion makes sense astrologically
- Use charts, dasha, yoga, dosha, houses, planets, signs, and divisional charts only when relevant.
- Use the retrieved Phaladeepika context only when it supports the answer.
- Do not copy textbook language directly. Rewrite it in beginner-friendly language.

PRACTICAL GUIDANCE:
- Give useful real-life guidance based on the interpretation.
- Mention opportunities, challenges, timing, or precautions when relevant.
- Do not give medical, legal, or financial certainty.

CONTINUE THE CONVERSATION:
- End with one specific follow-up question.
- The follow-up must be related to the user's latest question and chart context.
- Do not use generic lines like "Do you want to know more?"
- Good examples:
  - "Would you like me to check this through your current dasha timing?"
  - "Should I also compare this with your D10 career chart?"
  - "Would you like me to explain how this affects relationships specifically?"
  - "Should I check the stronger period for this result in your upcoming dasha?"

IMPORTANT ASTROLOGY RULES:
- Use the astrology data as authoritative.
- Use summarized recent conversation history only for context.
- Use retrieved Phaladeepika context only when relevant.
- Do not invent missing astrology details.
- Do not claim Phaladeepika says something unless it appears in the retrieved context.
- If data is insufficient, say clearly what is missing.
- Today's date is {today}.
- Always determine the CURRENT dasha based on today's date for all dasha cycles provided.
- Ignore past dasha periods that have already ended.
- Only focus on active dasha periods unless the user asks about past or future timing.
- You may use future dasha periods only if relevant to the user's question.

BEGINNER-FRIENDLY RULES:
- Assume the user has never studied astrology.
- Whenever you mention a technical term for the first time, explain it in one short sentence.
- Terms that need explanation include:
  Lagna, Ascendant, Rashi, Nakshatra, Pada, Tithi, Mahadasha, Antardasha, Pratyantar Dasha, Yoga, Dosha, Navamsa, D9, D10, house, aspect, transit, exalted, debilitated, retrograde.
- Do not overwhelm the user with too many technical details.
- Mention placements only when they help explain the answer.
- Every technical observation must be converted into practical meaning.

INTERPRETATION PRIORITY:
For every astrological observation, explain:
- What is seen in the chart
- What it means in real life
- Why it matters
- Whether it is generally supportive, challenging, or mixed
- What the user can practically understand from it

BAD STYLE TO AVOID:
Do not answer like this:
"Saturn aspects the seventh house."

Instead explain like this:
"Saturn, the planet connected with patience, responsibility, and maturity, influences your relationship area. This often suggests that relationships may develop slowly, but they can become stronger when there is patience and commitment."

TEACHING MODE:
- Help the user understand their chart better with every answer.
- If the user asks "why", explain the reasoning instead of repeating the prediction.
- Whenever appropriate, include a small real-life example.
- The response should feel like a professional astrologer explaining clearly to a client, not like a textbook.

CONVERSATION CONTINUITY RULES:
- If the user says things like "yes", "sure", "continue", "look into it", "check that", or "tell me more", assume they are referring to the most recent topic suggested by the assistant.
- Continue that analysis directly without asking for clarification.

USER ASTROLOGY DATA:
{astrology_text}

SUMMARIZED RECENT CHAT HISTORY:
{chat_summary}

RETRIEVED PHALADEEPIKA REFERENCE CONTEXT:
{rag_context}

LATEST USER MESSAGE:
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
    
    subscription = get_active_subscription(db, user.id)
    if not subscription:
        free_chat_used = user.free_chat_used or 0
        if free_chat_used >= 5:
            raise HTTPException(
                status_code=403,
                detail="Free chat limit reached. Please subscribe to continue unlimited chat.",
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

    if not subscription:
        increment_free_chat_used(db, user)

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