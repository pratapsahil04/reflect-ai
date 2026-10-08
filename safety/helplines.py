HELPLINES = {
    "IN": {
        "country": "India",
        "resources": [
            {
                "name": "Tele-MANAS",
                "phone": "14416",
                "description": "24×7 mental health support"
            },
            {
                "name": "Tele-MANAS alternate number",
                "phone": "1800-89-14416",
                "description": "24×7 mental health support"
            }
        ]
    },

    "US": {
        "country": "United States",
        "resources": [
            {
                "name": "988 Suicide & Crisis Lifeline",
                "phone": "988",
                "description": "Call or text 988"
            }
        ]
    }
}


def get_helplines(country_code: str = "IN") -> dict:
    """
    Return configured crisis resources for a country.
    """

    return HELPLINES.get(
        country_code.upper(),
        HELPLINES["IN"]
    )