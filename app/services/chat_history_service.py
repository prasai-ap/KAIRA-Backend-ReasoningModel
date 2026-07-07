from app.services.ai_service import generate_ai_response


def format_history_messages(history):
    if not history:
        return "No recent chat history available."

    return "\n".join(
        [f"{m.role.upper()}: {m.content}" for m in history]
    )


def summarize_chat_history(history):
    if not history:
        return "No recent chat summary available."

    history_text = format_history_messages(history)

    prompt = f"""
You are Kaira, a Vedic astrology AI assistant.

Summarize the recent conversation between the user and assistant.

The summary will be used only as context for the next astrology answer.

Write the summary in simple, clear language.

Include:
- the user's main concern
- astrology topics discussed
- important chart-related points mentioned
- any question the assistant suggested for follow-up
- useful context needed to continue the conversation

Remove:
- greetings
- repeated sentences
- unnecessary filler
- technical details that are not useful for the next answer

Do not add new astrology information.
Do not invent anything.
Use only the chat history below.

Recent chat history:
{history_text}

Summary:
""".strip()

    try:
        return generate_ai_response(prompt)
    except Exception as e:
        print(f"CHAT SUMMARY AI ERROR: {repr(e)}")

        return "Recent chat summary could not be generated. Continue using the latest user message and available astrology data."