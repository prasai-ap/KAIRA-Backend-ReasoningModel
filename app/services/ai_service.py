import os
from google import genai

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.1-flash")


def generate_ai_response(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
    )

    text = getattr(response, "text", None)
    if text and text.strip():
        return text.strip()

    try:
        return response.candidates[0].content.parts[0].text.strip()
    except Exception:
        return "I could not generate a response at this time."