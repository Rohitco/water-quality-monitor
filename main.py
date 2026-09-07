"""Water Quality Monitor — entry point.

Usage:
    python main.py
"""
from src.pipeline import run_pipeline

if __name__ == "__main__":
    run_pipeline(["data/source_lab_a.csv", "data/source_lab_b.csv"])
