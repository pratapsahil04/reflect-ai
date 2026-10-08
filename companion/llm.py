import os

from dotenv import load_dotenv
from google import genai

from companion.prompt import SYSTEM_PROMPT


load_dotenv()


api_key = os.getenv("GEMINI_API_KEY")


if not api_key:
    raise ValueError(
        "GEMINI_API_KEY is missing. "
        "Please add it to the .env file."
    )


client = genai.Client(
    api_key=api_key
)


def get_companion_response(user_message: str) -> str:

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": user_message
                        }
                    ]
                }
            ],
            config={
                "system_instruction": SYSTEM_PROMPT,
                "max_output_tokens": 500,
            }
        )

        return response.text

    except Exception as e:

        error_message = str(e)

        # ------------------------------------------
        # Gemini quota exceeded
        # ------------------------------------------

        if (
            "429" in error_message
            or "RESOURCE_EXHAUSTED" in error_message
            or "quota" in error_message.lower()
        ):

            return (
                "I'm temporarily unable to generate an AI reflection "
                "because the language model has reached its current "
                "usage limit.\n\n"
                "You can still use ReflectAI's journaling and safety "
                "features. Try again after the API quota resets."
            )

        # ------------------------------------------
        # Other Gemini errors
        # ------------------------------------------

        return (
            "I'm temporarily unable to generate a reflection. "
            "Please try again shortly."
        )