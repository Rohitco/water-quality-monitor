"""Orchestrates the water quality monitoring pipeline end to end."""
from src import db, ingest, star_schema
from src.validate import validate_samples


def run_pipeline(source_paths: list[str]) -> None:
    all_samples = ingest.ingest_and_consolidate(source_paths)
    clean, exceedances = validate_samples(all_samples)
    exceedance_ids = {e["sample_id"] for e in exceedances}

    schema = star_schema.build_star_schema(all_samples, exceedance_ids)
    star_schema.export_star_schema(schema)
    db.store_star_schema(schema)

    db.export_exceedances(exceedances)

    dashboard_data = db.build_dashboard_data(all_samples, exceedances)
    db.export_dashboard_data(dashboard_data)

    db.print_summary(all_samples, exceedances)
