"""Generates synthetic water quality sample data from two simulated external
lab sources, with deliberate guideline exceedances mixed in.
"""
import csv
import random
from datetime import date, timedelta

random.seed(11)

STATIONS = ["Station-North-1", "Station-North-2", "Station-East-1", "Station-South-1"]
PARAMETERS = {
    "pH": (7.4, 0.3),
    "Dissolved Arsenic": (2.0, 1.0),
    "Dissolved Copper": (0.8, 0.4),
    "Dissolved Lead": (0.4, 0.2),
    "Turbidity": (10.0, 4.0),
}
START_DATE = date(2026, 1, 5)


def make_sample(source, station, parameter, week_offset):
    mean, std = PARAMETERS[parameter]
    value = random.gauss(mean, std)

    # Inject occasional guideline exceedances
    if random.random() < 0.12:
        value = value * random.choice([2.2, 2.8, 3.5])

    sample_date = START_DATE + timedelta(weeks=week_offset)
    return {
        "source": source,
        "station": station,
        "parameter": parameter,
        "sample_date": sample_date.isoformat(),
        "value": round(max(value, 0), 3),
    }


def main():
    rows = []
    for week in range(12):  # 12 weeks of sampling
        for station in STATIONS:
            for parameter in PARAMETERS:
                source = "LabA" if hash((station, parameter)) % 2 == 0 else "LabB"
                rows.append(make_sample(source, station, parameter, week))

    lab_a = [r for r in rows if r["source"] == "LabA"]
    lab_b = [r for r in rows if r["source"] == "LabB"]

    with open("data/source_lab_a.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(lab_a[0].keys()))
        writer.writeheader()
        writer.writerows(lab_a)

    with open("data/source_lab_b.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(lab_b[0].keys()))
        writer.writeheader()
        writer.writerows(lab_b)

    print(f"Generated {len(lab_a)} rows -> data/source_lab_a.csv")
    print(f"Generated {len(lab_b)} rows -> data/source_lab_b.csv")


if __name__ == "__main__":
    main()
