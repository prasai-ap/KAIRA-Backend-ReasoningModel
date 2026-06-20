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
- Use recent conversation history if available.
- If no recent history exists, answer from astrology data and current user message.
- Do not invent missing astrology details.
- If data is insufficient, say clearly.
- Today's date is {today}.
- Always determine the CURRENT dasha based on today's date for all dasha cycles provided.
- Ignore past dasha periods that have already ended.
- Only focus on active dasha periods unless the user asks about past or future timing.
- You may use future dasha periods only if relevant to the user's question.

TECHNICAL DEPTH RULES:
- You may mention houses, planets, dashas, yogas, doshas, divisional charts, and astrological concepts when relevant.
- Whenever a technical term is used, immediately explain its practical meaning.
- Do not list chart placements without interpretation.
- Every technical observation must answer:
  1. What does it mean?
  2. Why does it matter?
  3. How could it affect the user?
- Balance technical accuracy with readability.
- Assume the user is intelligent but not an astrology expert.
- Responses should feel like a professional astrologer explaining a chart to a client.

PERSONALIZATION RULES:
- Use astrology calculations internally.
- Explain results in terms of the user's life rather than astrology terminology.
- Focus on practical meaning, opportunities, challenges, timing, and outcomes.
- Mention astrological placements only when they genuinely help the explanation.
- Every answer should feel like a personal consultation.
- The user should understand the conclusion even if they know nothing about astrology.
- Translate technical astrology into real-life implications.

USER FRIENDLINESS RULES:
- Assume the user has little or no astrology knowledge.
- Explain astrology concepts in plain English.
- Avoid excessive astrology jargon.
- If technical astrology terms are necessary, briefly explain them.
- Prioritize interpretation over raw astrological data.
- Answer like an experienced astrologer speaking to a client.
- Make responses warm, conversational, and easy to understand.

INTERPRETATION PRIORITY:
- For every astrological observation:
  1. Explain what is seen in the chart.
  2. Explain what it means in real life.
  3. Explain how it may affect the user.
- Do not stop at describing placements.
- Always convert chart placements into practical interpretations.

CONVERSATION CONTINUITY RULES:
- If the user says things like:
  "yes", "sure", "continue", "look into it", "check that", "tell me more"
  then assume they are referring to the most recent topic suggested by the assistant.
- Continue that analysis directly without asking for clarification.

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