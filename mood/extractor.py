import json
import re

from pydantic import BaseModel, Field

from companion.llm import client


class MoodResult(BaseModel):
    mood_score: int = Field(ge=1, le=10)
    primary_emotion: str
    secondary_emotions: list[str]
    themes: list[str]
    confidence: float = Field(ge=0.0, le=1.0)


def fallback_mood(text: str) -> MoodResult:
    """
    Local fallback used when Gemini is temporarily unavailable.
    This is intentionally simple and should not be treated as
    a clinical assessment.
    """

    text_lower = text.lower()

    positive_words = [
        "happy",
        "good",
        "great",
        "wonderful",
        "excited",
        "relaxed",
        "grateful",
        "joy",
        "love",
        "proud",
        "successful",
    ]

    negative_words = [
        "sad",
        "stress",
        "stressed",
        "exhausted",
        "angry",
        "frustrated",
        "disappointed",
        "lonely",
        "hopeless",
        "tired",
        "upset",
        "worried",
        "anxious",
    ]

    positive_count = sum(
        1 for word in positive_words
        if word in text_lower
    )

    negative_count = sum(
        1 for word in negative_words
        if word in text_lower
    )

    if positive_count > negative_count:
        mood_score = 7
        primary_emotion = "positive"
    elif negative_count > positive_count:
        mood_score = 4
        primary_emotion = "distress"
    else:
        mood_score = 5
        primary_emotion = "neutral"

    secondary_emotions = []

    emotion_map = {
        "stress": "stress",
        "stressed": "stress",
        "exhausted": "exhaustion",
        "tired": "tiredness",
        "happy": "happiness",
        "excited": "excitement",
        "sad": "sadness",
        "angry": "anger",
        "frustrated": "frustration",
        "disappointed": "disappointment",
        "lonely": "loneliness",
        "worried": "worry",
        "anxious": "anxiety",
        "relaxed": "relaxation",
        "grateful": "gratitude",
    }

    for word, emotion in emotion_map.items():
        if word in text_lower and emotion != primary_emotion:
            secondary_emotions.append(emotion)

    if not secondary_emotions:
        secondary_emotions = ["none clearly identified"]

    return MoodResult(
        mood_score=mood_score,
        primary_emotion=primary_emotion,
        secondary_emotions=secondary_emotions[:5],
        themes=["general reflection"],
        confidence=0.4,
    )


def extract_mood(user_message: str) -> MoodResult:

    prompt = f"""
Analyze the following journal entry.

Return ONLY valid JSON.

Use exactly these fields:

{{
    "mood_score": 1,
    "primary_emotion": "string",
    "secondary_emotions": ["string"],
    "themes": ["string"],
    "confidence": 0.0
}}

Rules:

- mood_score must be an integer from 1 to 10.
- 1 means very negative mood.
- 10 means very positive mood.
- primary_emotion should be the strongest emotion expressed.
- secondary_emotions should contain other emotions clearly present.
- themes should describe important topics in the entry.
- confidence must be between 0.0 and 1.0.
- Do not diagnose mental-health conditions.
- Do not infer medical conditions.
- Base the analysis only on the journal entry.

Journal entry:

{user_message}
"""

    try:

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config={
                "max_output_tokens": 300,
                "response_mime_type": "application/json",
            },
        )

        data = json.loads(response.text)

        return MoodResult.model_validate(data)

    except Exception as e:

        print(
            f"Mood extraction using Gemini failed: {e}"
        )

        print(
            "Using local fallback mood extraction."
        )

        return fallback_mood(user_message)