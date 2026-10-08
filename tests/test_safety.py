from safety.classifier import classify_with_rules


def test_normal_message_is_safe():
    assert classify_with_rules(
        "I had a stressful day at work."
    ) == "none"


def test_positive_message_is_safe():
    assert classify_with_rules(
        "Today was one of the best days I've had."
    ) == "none"


def test_explicit_suicidal_intent():
    assert classify_with_rules(
        "I want to kill myself."
    ) == "crisis"


def test_explicit_self_harm_intent():
    assert classify_with_rules(
        "I want to hurt myself."
    ) == "crisis"


def test_false_positive_plant():
    assert classify_with_rules(
        "My plant died yesterday."
    ) == "none"


def test_false_positive_movie():
    assert classify_with_rules(
        "The character died at the end of the movie."
    ) == "none"