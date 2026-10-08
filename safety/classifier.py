import re

from pydantic import BaseModel

from safety.rules import rule_based_crisis_check


class RiskResult(BaseModel):
    risk: str


VALID_RISKS = {
    "none",
    "elevated",
    "crisis"
}


# ---------------------------------------------------------
# Elevated-risk patterns
# ---------------------------------------------------------

ELEVATED_PATTERNS = [
    r"\beveryone would be better off without me\b",
    r"\bpeople would be better off without me\b",
    r"\bno one would miss me\b",
    r"\bnobody would miss me\b",
    r"\bi wish i could disappear\b",
    r"\bi want to disappear\b",
    r"\bi can't do this anymore\b",
    r"\bi cannot do this anymore\b",
    r"\bi am done with everything\b",
    r"\bi'm done with everything\b",
    r"\bi feel completely hopeless\b",
    r"\bi feel hopeless\b",
    r"\bi have no reason to live\b",
    r"\bthere is no reason to live\b",
    r"\bwhat is the point of living\b",
    r"\bwhat's the point of living\b",
    r"\bi don't want to be alive\b",
    r"\bi do not want to be alive\b",
]


# ---------------------------------------------------------
# Elevated classifier
# ---------------------------------------------------------

def rule_based_elevated_check(text: str) -> bool:
    """
    Detect concerning but non-explicit crisis language.
    """

    normalized = text.lower().strip()

    normalized = re.sub(
        r"\s+",
        " ",
        normalized
    )

    for pattern in ELEVATED_PATTERNS:

        if re.search(
            pattern,
            normalized
        ):
            return True

    return False


# ---------------------------------------------------------
# Complete local safety classifier
# ---------------------------------------------------------

def classify_risk(text: str) -> RiskResult:
    """
    Complete local safety classifier.

    Priority:

    1. Explicit crisis
    2. Elevated-risk language
    3. None
    """

    # High-confidence crisis detection

    if rule_based_crisis_check(text):

        return RiskResult(
            risk="crisis"
        )


    # Concerning but ambiguous language

    if rule_based_elevated_check(text):

        return RiskResult(
            risk="elevated"
        )


    # No detected safety concern

    return RiskResult(
        risk="none"
    )


# ---------------------------------------------------------
# Compatibility functions
# ---------------------------------------------------------

def classify_with_rules(text: str) -> str:
    """
    Compatibility wrapper for existing tests.
    """

    return classify_risk(text).risk


def classify_with_gemini(text: str) -> RiskResult:
    """
    Gemini is intentionally not used for the primary
    safety gate.

    The safety gate must remain functional even if
    the external LLM is unavailable.
    """

    return classify_risk(text)