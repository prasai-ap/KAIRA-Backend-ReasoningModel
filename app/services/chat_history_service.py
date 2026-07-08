from app.services.ai_service import generate_ai_response


def format_history_messages(history):
    if not history:
        return "No recent chat history in the last 30 days."

    return "\n".join(
        [f"{m.role.upper()}: {m.content}" for m in history]
    )


def summarize_chat_history(history):
    if not history:
        return "No recent chat summary available."

    history_text = format_history_messages(history)

    prompt = f"""
Summarize this recent astrology chat history.

Use only the messages below.

Keep:
- user's latest concern
- astrology topics discussed
- important preferences
- context useful for the next answer

Remove:
- greetings
- repeated filler
- unnecessary details

Chat history:
{history_text}
"""

    try:
        return generate_ai_response(prompt)
    except Exception:
        return "Recent chat summary could not be generated."