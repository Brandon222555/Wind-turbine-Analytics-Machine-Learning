import pandas as pd
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "wind_turbine")

# -----------------------------
# 1. CONNECT TO MYSQL
# -----------------------------
engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    echo=False
)

# -----------------------------
# 2. CLEAN TABLES BEFORE LOAD
# -----------------------------
tables = ["telemetry", "energy_yield", "weather", "downtime"]
with engine.begin() as conn:
    for t in tables:
        conn.execute(text(f"TRUNCATE TABLE {t};"))
    # turbines is NOT truncated — it stays permanent

print("Tables truncated. Ready to load fresh data.")

# -----------------------------
# 3. CHUNKED CSV LOADER
# -----------------------------


def load_csv_in_chunks(csv_path, table_name, chunksize=50000):
    print(f"\nLoading {csv_path} into {table_name}...")
    for chunk in pd.read_csv(csv_path, chunksize=chunksize):
        # Convert timestamps to proper datetime
        if "ts" in chunk.columns:
            chunk["ts"] = pd.to_datetime(chunk["ts"], errors="coerce")

        if "event_start" in chunk.columns:
            chunk["event_start"] = pd.to_datetime(
                chunk["event_start"], errors="coerce")

        if "event_end" in chunk.columns:
            chunk["event_end"] = pd.to_datetime(
                chunk["event_end"], errors="coerce")

        chunk.to_sql(table_name, engine, if_exists="append", index=False)
        print(f"Inserted {len(chunk)} rows into {table_name}")


# -----------------------------
# 4. LOAD ALL DATA TABLES
# -----------------------------
load_csv_in_chunks("data/telemetry.csv", "telemetry")
load_csv_in_chunks("data/yield.csv", "energy_yield")
load_csv_in_chunks("data/weather.csv", "weather")
load_csv_in_chunks("data/downtime.csv", "downtime")

print("\nAll data tables loaded successfully!")

# -----------------------------
# 5. LOAD TURBINES SAFELY (NO DUPLICATES)
# -----------------------------
turbines = pd.read_csv("data/turbines.csv")

with engine.begin() as conn:
    for _, row in turbines.iterrows():
        conn.execute(text("""
            INSERT INTO turbines (turbine_id, rated_power_kw, hub_height_m, model)
            VALUES (:turbine_id, :rated_power_kw, :hub_height_m, :model)
            ON DUPLICATE KEY UPDATE
                rated_power_kw = VALUES(rated_power_kw),
                hub_height_m = VALUES(hub_height_m),
                model = VALUES(model);
        """), row.to_dict())

print("Turbines table updated safely (no duplicates).")
print("\nLOAD COMPLETE — Your database is now clean and ready.")
