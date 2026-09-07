"""Guideline threshold reference. See README.md for sourcing and caveats —
these are simplified, static representative values for demonstration, not a
substitute for actual hardness-adjusted regulatory guidelines.
"""

# parameter -> (min, max) acceptable range; None means no lower/upper bound
GUIDELINES = {
    "pH": (6.5, 9.0),
    "Dissolved Arsenic": (None, 5.0),
    "Dissolved Copper": (None, 2.0),
    "Dissolved Lead": (None, 1.0),
    "Turbidity": (None, 25.0),
}


def get_guideline(parameter: str) -> tuple:
    if parameter not in GUIDELINES:
        raise KeyError(f"No guideline defined for parameter: {parameter}")
    return GUIDELINES[parameter]
