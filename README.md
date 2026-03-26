# 🌬️ Wind Turbine Analytics & Machine Learning
End‑to‑End Data Engineering + Data Science Project
https://images.unsplash.com/photo-1509395176047-4a66953fd231?auto=format&fit=crop&w=1350&q=80

# 🏷️ Badges
https://img.shields.io/badge/Python-3.10-blue
https://img.shields.io/badge/Database-MySQL-orange
https://img.shields.io/badge/Library-Pandas-yellow
https://img.shields.io/badge/ML-Scikit--Learn-green
https://img.shields.io/badge/Discipline-Data%20Engineering-red
https://img.shields.io/badge/Analysis-Time%20Series-purple


# 📌 Overview
This project simulates a full wind farm analytics pipeline, from raw turbine telemetry to machine‑learning models that predict power output and downtime.

It demonstrates real‑world skills used in:

Renewable energy analytics

IoT sensor data processing

Data engineering

Machine learning

Time‑series forecasting

Operational performance monitoring

You’ll find everything from ETL pipelines to SQL views, ML models, and visual insights.


# 🧱 Project Architecture
Code
wind-turbine-analytics/
│
├── data/                     # Raw + processed CSVs
├── sql/                      # Schema + SQL views
├── analysis/                 # Python analysis scripts
├── src/                      # Utility modules (db, plotting, ETL)
├── plots/                    # Saved visualizations
├── load_to_mysql.py          # Chunked ETL loader
└── README.md                 # Project documentation


# 🗄️ Database & ETL Pipeline
MySQL Schema Includes:
Table	Description
telemetry	10‑minute turbine telemetry (wind, rotor speed, power)
energy_yield	Energy produced per interval
weather	Temperature, pressure, icing, precipitation
downtime	Faults, maintenance, and outage events
turbines	Turbine metadata (model, height, rated power)

ETL Loader Features
Chunked ingestion (50k rows at a time)

Automatic timestamp parsing

Duplicate‑safe turbine loading

Clean table resets for repeatable runs

Production‑style SQLAlchemy engine

# 📊 Analytics & Visualizations
1. Daily Energy Yield
Shows daily production trends for each turbine.

2. Monthly Capacity Factor
Evaluates turbine efficiency relative to rated power.

3. Empirical Power Curve
Wind speed → power output relationship.

4. Lost Energy Estimation
Rolling‑median baseline to detect underperformance.

5. Weather Impact
Correlation between power, wind, temperature, icing, etc.

6. Downtime Analysis
Hourly downtime classification + lost energy.

All plots are saved in the plots/ directory.

# 🤖 Machine Learning Models
A. Power Output Prediction (Regression)
Model: RandomForestRegressor
Features:

Wind speed

Temperature

Icing flag

Output: Predicted power (kW)

B. Downtime Classification (Logistic Regression)
Predicts whether a turbine is likely to be in downtime based on weather conditions.

# 🧠 Key Insights
Power output strongly correlates with wind speed and icing conditions.

Rolling‑median baseline effectively identifies underperformance.

Downtime events cluster around low‑temperature, high‑icing periods.

ML models achieve strong predictive performance with minimal features.

# 🛠️ Tech Stack
Python: Pandas, NumPy, Scikit‑Learn, Matplotlib, Seaborn

Database: MySQL

Tools: SQLAlchemy, Jupyter, VS Code

Concepts: ETL, ML, Time‑Series, Feature   Engineering

# 🚀 How to Run the Project
1. Clone the repo
bash
git clone https://github.com/yourusername/wind-turbine-analytics.git
cd wind-turbine-analytics
2. Install dependencies
bash
pip install -r requirements.txt
3. Load data into MySQL
bash
python load_to_mysql.py
4. Run the analysis
bash
python analysis/analysis_production.py

