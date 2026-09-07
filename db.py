"""Persists the fact/dimension tables to SQLite for local querying, and
generates the run summary plus dashboard JSON for the HTML visualization.
"""
import csv
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "output" / "water_quality.db"
EXCEEDANCES_CSV = Path(__file__).resolve().parent.parent / "output" / "exceedances_for_review.csv"
DASHBOARD_JSON = Path(__file__).resolve().parent.parent / "output" / "dashboard_data.json"


def store_star_schema(schema: dict) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DROP TABLE IF EXISTS fact_samples")
    conn.execute("DROP TABLE IF EXISTS dim_station")
    conn.execute("DROP TABLE IF EXISTS dim_parameter")
    conn.execute("DROP TABLE IF EXISTS dim_date")

    conn.execute("""CREATE TABLE fact_samples (
        sample_id TEXT, station_id TEXT, parameter_id TEXT, date_id TEXT,
        source TEXT, value REAL, is_exceedance INTEGER)""")
    conn.execute("CREATE TABLE dim_station (station_id TEXT, station_name TEXT)")
    conn.execute("CREATE TABLE dim_parameter (parameter_id TEXT, parameter_name TEXT)")
    conn.execute("CREATE TABLE dim_date (date_id TEXT, date TEXT, year TEXT, month TEXT, week_of_year INTEGER)")

    conn.executemany(
        "INSERT INTO fact_samples VALUES (:sample_id, :station_id, :parameter_id, :date_id, :source, :value, :is_exceedance)",
        schema["fact_samples"],
    )
    conn.executemany("INSERT INTO dim_station VALUES (:station_id, :station_name)", schema["dim_station"])
    conn.executemany("INSERT INTO dim_parameter VALUES (:parameter_id, :parameter_name)", schema["dim_parameter"])
    conn.executemany(
        "INSERT INTO dim_date VALUES (:date_id, :date, :year, :month, :week_of_year)", schema["dim_date"]
    )
    conn.commit()
    conn.close()


def export_exceedances(exceedances: list[dict]) -> None:
    EXCEEDANCES_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["sample_id", "source", "station", "parameter", "sample_date", "value", "reason"]
    with EXCEEDANCES_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(exceedances)

    # Also write for the standalone HTML dashboard to consume directly.
    exceedances_js_path = Path(__file__).resolve().parent.parent / "dashboard" / "exceedances.js"
    exceedances_js_path.parent.mkdir(parents=True, exist_ok=True)
    with exceedances_js_path.open("w", encoding="utf-8") as f:
        f.write("const EXCEEDANCES = ")
        json.dump(exceedances, f, indent=2)
        f.write(";\n")


def build_dashboard_data(all_samples: list[dict], exceedances: list[dict]) -> dict:
    by_station = defaultdict(lambda: {"total": 0, "exceedances": 0})
    by_parameter = defaultdict(lambda: {"total": 0, "exceedances": 0})
    exceedance_ids = {e["sample_id"] for e in exceedances}

    for s in all_samples:
        by_station[s["station"]]["total"] += 1
        by_parameter[s["parameter"]]["total"] += 1
        if s["sample_id"] in exceedance_ids:
            by_station[s["station"]]["exceedances"] += 1
            by_parameter[s["parameter"]]["exceedances"] += 1

    return {
        "total_samples": len(all_samples),
        "total_exceedances": len(exceedances),
        "by_station": by_station,
        "by_parameter": by_parameter,
    }


def export_dashboard_data(data: dict) -> None:
    DASHBOARD_JSON.parent.mkdir(parents=True, exist_ok=True)
    with DASHBOARD_JSON.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    # Also write as an embedded JS file so the dashboard works standalone
    # (double-click to open) without hitting file:// fetch/CORS restrictions.
    data_js_path = Path(__file__).resolve().parent.parent / "dashboard" / "data.js"
    data_js_path.parent.mkdir(parents=True, exist_ok=True)
    with data_js_path.open("w", encoding="utf-8") as f:
        f.write("const DASHBOARD_DATA = ")
        json.dump(data, f, indent=2)
        f.write(";\n")


def print_summary(all_samples: list[dict], exceedances: list[dict]) -> None:
    total = len(all_samples)
    exceed_count = len(exceedances)
    reason_counts = Counter(e["parameter"] for e in exceedances)

    print("=== Water Quality Monitor — Run Summary ===")
    print(f"Samples processed (2 external sources consolidated): {total}")
    print(f"Guideline exceedances flagged: {exceed_count}  ({exceed_count/total*100:.1f}%)")
    for parameter, count in reason_counts.most_common():
        print(f"  - {parameter}: {count}")
    print("Star schema exported: output/star_schema/ (fact_samples, dim_station, dim_parameter, dim_date)")
    print("Exceedance queue exported: output/exceedances_for_review.csv")
    print("Dashboard data exported: output/dashboard_data.json")
