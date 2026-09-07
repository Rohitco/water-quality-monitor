from src.star_schema import build_star_schema


def make_samples():
    return [
        {"sample_id": "S-1", "source": "LabA", "station": "Station-A", "parameter": "pH",
         "sample_date": "2026-01-05", "value": "7.4"},
        {"sample_id": "S-2", "source": "LabB", "station": "Station-B", "parameter": "Turbidity",
         "sample_date": "2026-01-12", "value": "30.0"},
    ]


def test_dimension_tables_have_unique_entries():
    schema = build_star_schema(make_samples(), exceedance_ids=set())
    assert len(schema["dim_station"]) == 2
    assert len(schema["dim_parameter"]) == 2
    assert len(schema["dim_date"]) == 2


def test_fact_table_has_one_row_per_sample():
    schema = build_star_schema(make_samples(), exceedance_ids=set())
    assert len(schema["fact_samples"]) == 2


def test_fact_table_foreign_keys_resolve():
    schema = build_star_schema(make_samples(), exceedance_ids=set())
    station_ids = {row["station_id"] for row in schema["dim_station"]}
    parameter_ids = {row["parameter_id"] for row in schema["dim_parameter"]}
    date_ids = {row["date_id"] for row in schema["dim_date"]}

    for fact in schema["fact_samples"]:
        assert fact["station_id"] in station_ids
        assert fact["parameter_id"] in parameter_ids
        assert fact["date_id"] in date_ids


def test_exceedance_flag_set_correctly():
    schema = build_star_schema(make_samples(), exceedance_ids={"S-2"})
    flags = {row["sample_id"]: row["is_exceedance"] for row in schema["fact_samples"]}
    assert flags["S-1"] == 0
    assert flags["S-2"] == 1
