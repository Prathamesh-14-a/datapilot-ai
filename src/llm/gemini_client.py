import os
import time
from dotenv import load_dotenv
from google import genai
import logging

logger = logging.getLogger(__name__)

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")

client = genai.Client(api_key=api_key)


def _is_transient_error(error: Exception) -> bool:
    message = str(error).lower()
    return any(
        token in message
        for token in (
            "503",
            "unavailable",
            "temporarily unavailable",
            "high demand",
            "rate limit",
            "resource exhausted",
        )
    )


def _retry_delay_seconds(attempt):
    return min(30.0, 5.0 * (attempt + 1))


def generate_response(prompt: str):
    last_error = None

    for attempt in range(5):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )

            return response.text

        except Exception as error:
            last_error = error

            if not _is_transient_error(error) or attempt == 2:
                break

            delay = _retry_delay_seconds(attempt)
            logger.warning(
    f"Gemini transient error on attempt {attempt + 1}: {error}"
)
            time.sleep(delay)

    logger.error(f"Gemini Error: {last_error}")

    return (
        "AI service is temporarily unavailable. "
        "Please try again in a few minutes."
    )
