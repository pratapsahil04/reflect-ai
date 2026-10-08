import re


# These patterns are intentionally conservative.
# They are a first-pass safety screen, not a clinical classifier.

CRISIS_PATTERNS = [
    # Suicide / self-harm intent
    r"\bi want to die\b",
    r"\bi wanna die\b",
    r"\bi wish i was dead\b",
    r"\bi wish i were dead\b",
    r"\bi want to kill myself\b",
    r"\bi wanna kill myself\b",
    r"\bi am going to kill myself\b",
    r"\bi'm going to kill myself\b",
    r"\bi will kill myself\b",
    r"\bi'm going to end my life\b",
    r"\bi want to end my life\b",
    r"\bi am going to end my life\b",
    r"\bi plan to kill myself\b",
    r"\bi plan to end my life\b",
    r"\bi have a plan to kill myself\b",
    r"\bi have a plan to end my life\b",

    # Explicit self-harm intent
    r"\bi want to hurt myself\b",
    r"\bi wanna hurt myself\b",
    r"\bi am going to hurt myself\b",
    r"\bi'm going to hurt myself\b",
    r"\bi plan to hurt myself\b",
    r"\bi intend to hurt myself\b",

    # Immediate danger language
    r"\bi am suicidal\b",
    r"\bi'm suicidal\b",
    r"\bi am about to kill myself\b",
    r"\bi'm about to kill myself\b",
    r"\bi am about to hurt myself\b",
    r"\bi'm about to hurt myself\b",
]


def normalize_text(text: str) -> str:
    """
    Normalize user input for rule matching.
    """
    text = text.lower().strip()

    # Collapse repeated whitespace.
    text = re.sub(r"\s+", " ", text)

    return text


def rule_based_crisis_check(text: str) -> bool:
    """
    Return True when a high-confidence crisis phrase is detected.
    """
    normalized = normalize_text(text)

    for pattern in CRISIS_PATTERNS:
        if re.search(pattern, normalized):
            return True

    return False