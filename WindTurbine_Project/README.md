# Wind Turbine Analytics Project

A Python-based data analytics project for monitoring and analyzing wind farm performance. This project generates realistic wind farm telemetry, stores it in a MySQL database, and applies machine learning to predict power output and detect downtime.

---

## Project Overview

This project covers the full data pipeline for a simulated 5-turbine wind farm:

- Synthetic data generation (weather, telemetry, energy yield, downtime events)
- MySQL database schema with views for hourly aggregation
- Exploratory data analysis in Jupyter notebooks
- Time series analysis of energy production and capacity factor
- Downtime and lost energy estimation
- Weather impact correlation analysis
- Machine learning models for power prediction and downtime classification

---

## Project Structure

```
WindTurbine_Project/
│
├── analysis.py                        # Main analytics and ML script
├── generate_mock_windfarm_data.py     # Generates synthetic wind farm CSV data
├── test_connection.py                 # Tests MySQL database connectivity
├── schema.sql                         # Full MySQL schema (tables + views)
│
├── data/
│   ├── load_to_mysql.py               # Loads CSV files into MySQL
│   └── *.csv                          # Generated data files (git-ignored)
│
├── notebooks/
│   ├── 01_data_exploration.ipynb      # Initial data exploration
│   └── 02_weather_downtime_impact.ipynb  # Weather & downtime analysis
│
├── .env.example                       # Template for database credentials
├── .gitignore
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Brandon222555/Python-projects.git
cd Python-projects/WindTurbine_Project
```

### 2. Install dependencies

```bash
pip install pandas numpy sqlalchemy mysql-connector-python scikit-learn matplotlib seaborn python-dotenv jupyter
```

### 3. Set up your credentials

```bash
cp .env.example .env
```

Edit `.env` with your actual MySQL details:

```
DB_USER=root
DB_PASSWORD=your_password_here
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=wind_turbine
```

### 4. Set up the MySQL database

Run `schema.sql` in your MySQL client to create all tables and views:

```bash
mysql -u root -p wind_turbine < schema.sql
```

### 5. Generate mock data

```bash
python generate_mock_windfarm_data.py
```

This creates CSV files in the `data/` folder.

### 6. Load data into MySQL

```bash
python data/load_to_mysql.py
```

### 7. Test your connection

```bash
python test_connection.py
```

### 8. Run the analysis

```bash
python analysis.py
```

Or explore the Jupyter notebooks:

```bash
jupyter notebook notebooks/
```

---

## What the Analysis Produces

- **Daily Energy Yield** — Line chart of kWh output per turbine over the year
- **Monthly Capacity Factor** — How efficiently each turbine uses its rated capacity
- **Empirical Power Curve** — Relationship between wind speed and power output
- **Lost Energy Estimation** — kWh lost per turbine due to downtime
- **Weather Correlation Heatmap** — Impact of wind speed, temperature, and icing on power
- **ML Power Prediction** — Random Forest model predicting power from weather (R² score)
- **ML Downtime Classification** — Logistic Regression predicting downtime events

---

## Database Schema

The MySQL database contains five tables and a set of views for hourly aggregation:

| Table | Description |
|-------|-------------|
| `turbines` | Static turbine metadata |
| `telemetry` | 10-minute power and rotor readings per turbine |
| `energy_yield` | 10-minute energy output per turbine |
| `weather` | 10-minute site-level weather readings |
| `downtime` | Downtime events with type, cause, and severity |

The main analytical view is `v_turbine_hourly`, which joins all tables into a single hourly dataset used by `analysis.py`.

---

## Turbine Specs (Simulated)

| Parameter | Value |
|-----------|-------|
| Turbines | 5 (T01–T05) |
| Rated Power | 3,000 kW |
| Hub Height | 100 m |
| Model | WT-3MW |
| Data Resolution | 10 minutes |
| Time Period | Jan–Dec 2023 |

---

## Dependencies

- `pandas`, `numpy` — Data manipulation
- `sqlalchemy`, `mysql-connector-python` — Database connection
- `scikit-learn` — Machine learning (Random Forest, Logistic Regression)
- `matplotlib`, `seaborn` — Visualization
- `python-dotenv` — Secure credential loading
- `jupyter` — Notebook environment

---

## Security Note

Database credentials are loaded from a `.env` file and are never committed to this repository. See `.env.example` for the required format.
