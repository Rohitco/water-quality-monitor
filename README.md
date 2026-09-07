# Environmental Water Quality Monitoring & Visualization Tool

A Python data pipeline and Power BI-ready data model for monitoring surface
water quality samples against regulatory guideline thresholds — built to
demonstrate the same data ingestion, modeling, and visualization workflow
used for environmental water quality dashboards on mining/infrastructure
projects.

## Important honesty note

This environment doesn't have Power BI Desktop, so I could not build or test
an actual `.pbix` file. What's real and tested here:

- A working Python pipeline that ingests, consolidates, and validates water
  quality data from multiple simulated external sources (two lab feeds).
- A genuine **dimensional star-schema data model** (fact + dimension tables),
  exported as clean CSVs — exactly the shape of data you'd import into Power
  BI and build relationships/measures on top of.
- **DAX measure definitions** (`dax_measures.txt`) written by hand, in valid
  DAX syntax, for the standard KPIs this kind of dashboard needs (exceedance
  rate, average parameter value, station-level rollups). These are **not
  executed or validated against a live Power BI/Analysis Services engine** —
  they're provided as reference formulas that would be pasted into Power BI
  Desktop against the star schema below.
- A **standalone HTML/Chart.js dashboard** (`dashboard/index.html`) that
  reads the pipeline's output and renders the same KPIs interactively in a
  browser — a working visualization, built as a stand-in for a Power BI
  report since Power BI itself isn't available here.

## Why this exists

Environmental monitoring teams pull water quality samples from multiple labs
and field sources, need to flag guideline exceedances quickly, and need that
data modeled cleanly enough to drive a Power BI dashboard used by both
technical and non-technical stakeholders. This project builds that pipeline
end to end.

## Guideline thresholds used

Simplified, representative thresholds for parameters commonly tracked in
Canadian freshwater aquatic life guidelines (CCME), used here for
demonstration only — **not a substitute for actual regulatory guideline
values**, several of which (e.g., copper, lead) are hardness-adjusted in
practice rather than fixed constants:

| Parameter | Threshold used | Basis |
|---|---|---|
| pH | 6.5 – 9.0 | CCME freshwater aquatic life range |
| Dissolved Arsenic | 5 µg/L | CCME long-term guideline |
| Dissolved Copper | 2 µg/L (simplified, static) | CCME guideline is hardness-adjusted in practice |
| Dissolved Lead | 1 µg/L (simplified, static) | CCME guideline is hardness-adjusted in practice |
| Turbidity | 25 NTU | Common operational threshold |

## Pipeline

1. **Ingest** (`src/ingest.py`) — reads and consolidates samples from two
   simulated external lab sources into one unified schema.
2. **Validate** (`src/guidelines.py`, `src/validate.py`) — checks each sample
   against its parameter's guideline threshold, flagging exceedances.
3. **Star schema** (`src/star_schema.py`) — builds `fact_samples`,
   `dim_station`, `dim_parameter`, and `dim_date` tables, exported to
   `output/star_schema/` as CSVs ready for Power BI import.
4. **Report** — prints a summary (samples processed, exceedance rate by
   parameter and station) and exports `output/exceedances_for_review.csv`.
5. **Dashboard** (`dashboard/index.html`) — open directly in a browser; reads
   `output/dashboard_data.json` and renders exceedance trends by station and
   parameter.

## Run it

```bash
pip install -r requirements.txt
python main.py
```

Then open `dashboard/index.html` in a browser.

## Test it

```bash
pytest tests/ -v
```

## Stack

Python · SQLite · pytest · Chart.js (dashboard) · DAX (reference measures, untested)
