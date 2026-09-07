"""Builds a dimensional star-schema data model from consolidated, validated
water quality samples — fact_samples plus dim_station, dim_parameter, and
dim_date — exported as CSVs ready to import directly into Power BI and wire
up with relationships.
"""
import csv
from pathlib import Path

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "output" / "star_schema"


def build_star_schema(all_samples: list[dict], exceedance_ids: set[str]) -> dict:
    stations = sorted({s["station"] for s in all_samples})
    parameters = sorted({s["parameter"] for s in all_samples})
    dates = sorted({s["sample_date"] for s in all_samples})

    dim_station = [{"station_id": f"ST-{i+1:02d}", "station_name": s} for i, s in enumerate(stations)]
    station_lookup = {row["station_name"]: row["station_id"] for row in dim_station}

    dim_parameter = [{"parameter_id": f"PM-{i+1:02d}", "parameter_name": p} for i, p in enumerate(parameters)]
    parameter_lookup = {row["parameter_name"]: row["parameter_id"] for row in dim_parameter}

    dim_date = [
        {
            "date_id": f"DT-{i+1:04d}",
            "date": d,
            "year": d[:4],
            "month": d[5:7],
            "week_of_year": i + 1,
        }
        for i, d in enumerate(dates)
    ]
    date_lookup = {row["date"]: row["date_id"] for row in dim_date}

    fact_samples = [
        {
            "sample_id": s["sample_id"],
            "station_id": station_lookup[s["station"]],
            "parameter_id": parameter_lookup[s["parameter"]],
            "date_id": date_lookup[s["sample_date"]],
            "source": s["source"],
            "value": s["value"],
            "is_exceedance": 1 if s["sample_id"] in exceedance_ids else 0,
        }
        for s in all_samples
    ]

    return {
        "fact_samples": fact_samples,
        "dim_station": dim_station,
        "dim_parameter": dim_parameter,
        "dim_date": dim_date,
    }


def export_star_schema(schema: dict) -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for table_name, rows in schema.items():
        path = OUTPUT_DIR / f"{table_name}.csv"
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
