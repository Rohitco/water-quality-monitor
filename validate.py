"""Flags samples that exceed their parameter's guideline threshold."""
from src.guidelines import get_guideline


def check_exceedance(sample: dict) -> str | None:
    """Returns a reason string if the sample exceeds its guideline, else None."""
    parameter = sample["parameter"]
    value = float(sample["value"])
    low, high = get_guideline(parameter)

    if low is not None and value < low:
        return f"Below guideline minimum ({value} < {low})"
    if high is not None and value > high:
        return f"Exceeds guideline maximum ({value} > {high})"
    return None


def validate_samples(samples: list[dict]) -> tuple[list[dict], list[dict]]:
    """Returns (clean_samples, exceedances). Each exceedance dict includes
    the original sample plus a 'reason' field."""
    clean = []
    exceedances = []
    for sample in samples:
        reason = check_exceedance(sample)
        if reason:
            exceedances.append({**sample, "reason": reason})
        else:
            clean.append(sample)
    return clean, exceedances
