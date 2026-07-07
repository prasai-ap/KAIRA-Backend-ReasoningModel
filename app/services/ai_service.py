import os
import time
import requests
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError, ServerError

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash-lite")

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "mistral")

gemini_client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY else None


def extract_gemini_text(response) -> str:
    text = getattr(response, "text", None)

    if text and text.strip():
        return text.strip()

    try:
        text = response.candidates[0].content.parts[0].text
        if text and text.strip():
            return text.strip()
    except Exception:
        pass

    raise Exception("Gemini returned an empty response")


def generate_with_gemini(prompt: str) -> str:
    if not gemini_client:
        raise Exception("GEMINI_API_KEY is missing from .env")

    last_error = None

    for attempt in range(2):
        try:
            response = gemini_client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
            )

            return extract_gemini_text(response)

        except ServerError as e:
            last_error = e
            print(f"GEMINI SERVER ERROR | attempt={attempt + 1} | error={e}")
            time.sleep(2 * (attempt + 1))

        except APIError as e:
            last_error = e
            print(f"GEMINI API ERROR | error={e}")
            break

        except Exception as e:
            last_error = e
            print(f"GEMINI UNEXPECTED ERROR | error={e}")
            break

    raise Exception(f"Gemini failed: {last_error}")


def generate_with_ollama(prompt: str) -> str:
    url = f"{OLLAMA_BASE_URL}/api/chat"

    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 900,
        },
    }

    last_error = None

    for attempt in range(2):
        try:
            response = requests.post(
                url,
                json=payload,
                timeout=180,
            )

            if response.status_code != 200:
                raise Exception(
                    f"Ollama error {response.status_code}: {response.text}"
                )

            data = response.json()
            text = data.get("message", {}).get("content")

            if text and text.strip():
                return text.strip()

            raise Exception("Ollama returned an empty response")

        except Exception as e:
            last_error = e
            print(f"OLLAMA ERROR | attempt={attempt + 1} | error={e}")
            time.sleep(2)

    raise Exception(f"Ollama failed: {last_error}")


def generate_ai_response(prompt: str) -> str:
    """
    Main AI function used by chat_service.py.

    Same prompt flow:
    1. chat_service.py builds one final Kaira prompt.
    2. Gemini receives that exact prompt.
    3. If Gemini fails, Ollama receives that exact same prompt.
    """

    try:
        print("Trying Gemini...")
        return generate_with_gemini(prompt)

    except Exception as gemini_error:
        print(f"Gemini failed. Falling back to Ollama. Error: {gemini_error}")

    try:
        print("Trying Ollama...")
        return generate_with_ollama(prompt)

    except Exception as ollama_error:
        print(f"Ollama also failed. Error: {ollama_error}")
        raise Exception(
            f"Both Gemini and Ollama failed. Last error: {ollama_error}"
        )