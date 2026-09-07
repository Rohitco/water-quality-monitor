"""Ingests and consolidates water quality samples from multiple external
lab sources into one unified schema.
"""
import csv
from pathlib import Path


def ingest_source(path: str) -> list[dict]:
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Source not found: {path}")
    with p.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def ingest_and_consolidate(paths: list[str]) -> list[dict]:
    """Reads multiple external sources and returns one consolidated list,
    with a stable synthetic sample_id assigned for downstream keying."""
    consolidated = []
    for path in paths:
        consolidated.extend(ingest_source(path))

    for i, row in enumerate(consolidated, start=1):
        row["sample_id"] = f"S-{i:05d}"

    return consolidated
