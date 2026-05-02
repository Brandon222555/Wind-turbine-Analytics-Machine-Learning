# Wind Turbine Analytics & Machine Learning Platform

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-Database-blue?logo=mysql&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange?logo=scikit-learn&logoColor=white)
![Records](https://img.shields.io/badge/Records-525K+-brightgreen)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)

> Production-style end-to-end data pipeline for fleet-wide wind turbine performance analysis. Ingests 525,000+ records of 10-minute telemetry, weather, and energy-yield data into a normalized MySQL schema — then applies ML models to predict power output, classify faults, and quantify energy recovery opportunities.

---

## What This Project Does

Energy companies operate fleets of turbines generating terabytes of sensor data every day. The challenge isn't collecting the data — it's building a pipeline that ingests it reliably, stores it queryably, and surfaces the insights that drive maintenance decisions.

This project simulates that workflow end-to-end: from raw telemetry ingestion through fault classification and executive-level reporting.

---

## Key Results

- **525,000+ records** ingested via chunked bulk loading into normalized MySQL schema
- **5% energy recovery** opportunity identified via rolling-median anomaly baselines
- **Fault classification** model correctly flags underperforming turbines before full downtime
- **12 publication-quality visualizations** for stakeholder reporting

---

## Pipeline Architecture

```
Raw Data (CSV/telemetry)
        ↓
   ETL Layer (Python + SQLAlchemy)
   • Chunked loading (memory-safe for large files)
   • Data quality checks + null handling
   • Schema validation
        ↓
   MySQL Schema (normalized)
   • turbines table
   • readings table (10-min intervals)
   • weather table
   • fault_events table
   • Analytical SQL views (KPIs, aggregations)
        ↓
   Analytics Layer
   • Fleet-wide KPIs: availability, capacity factor, fault rate
   • Rolling-median anomaly detection
   • Power curve deviation analysis
        ↓
   ML Models
   • Power output regression (Random Forest)
   • Downtime classification (Logistic Regression)
        ↓
   Reporting
   • 12 charts: heatmaps, time-series, anomaly plots, scatter
```

---

## Technical Highlights

**ETL Design**
- Chunked loading (`chunksize=10000`) handles files too large to fit in memory
- SQLAlchemy ORM for schema management and connection pooling
- Idempotent pipeline — safe to re-run without duplicate inserts

**SQL Schema**
- Normalized to 3NF: no redundant data across turbine, weather, and readings tables
- Pre-built analytical views for fleet KPIs — downstream dashboards query views, not raw tables
- Indexed on `turbine_id` + `timestamp` for fast time-range queries

**Anomaly Detection**
- Rolling 7-day median baseline per turbine
- Flag readings deviating >2σ from expected power output
- Identified 5% energy recovery opportunity across the fleet

**ML Models**
- Random Forest regressor for power output prediction (RMSE + R² metrics)
- Logistic Regression classifier for downtime event prediction (precision/recall on fault class)

---

## Tech Stack

```
Python 3.8+        — core language
Pandas / NumPy     — data processing
SQLAlchemy         — ORM + connection management
MySQL              — relational data warehouse
Scikit-Learn       — ML models
Matplotlib/Seaborn — visualization
```

---

## Project Structure

```
Wind-turbine-Analytics-Machine-Learning/
├── data/              # Raw telemetry CSVs
├── etl/               # Ingestion scripts + chunked loader
├── sql/               # Schema DDL + analytical views
├── models/            # ML training + evaluation
├── visualizations/    # Chart outputs
├── notebooks/         # Exploratory analysis
└── main.py            # Full pipeline runner
```

---

## Business Impact Framing

This project is built the way a senior Data/Analytics Engineer would build it — not as a notebook experiment, but as a maintainable, queryable system:

| Decision | Why it matters |
|---|---|
| Chunked ETL loading | Handles real-world file sizes without OOM crashes |
| Analytical SQL views | Downstream users query views — no re-engineering needed when raw schema changes |
| Rolling baselines over static thresholds | Adapts to seasonal variation in wind patterns |
| Fault recall optimization | False negatives (missed faults) cost more than false positives in energy ops |

---

## Author

**Brandon Quansah** — Data Scientist / Data Engineer | Physics B.S., Rowan University

[LinkedIn](https://linkedin.com/in/brandonquansah) · [GitHub](https://github.com/Brandon222555) · quansahb21@gmail.com
