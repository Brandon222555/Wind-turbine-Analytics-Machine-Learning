"""
load_to_db.py
-------------
Loads generated CSV data into a local SQLite database (no server needed).
SQLite is built into Python — nothing to install or configure.
"""

import pandas as pd
import sqlite3
import os

DB_PATH = "data/stocks.db"

print("Connecting to SQLite database...")
conn = sqlite3.connect(DB_PATH)

# Apply schema
with open("schema.sql", "r") as f:
    conn.executescript(f.read())
print("Schema applied.")

# Load raw stocks
print("Loading stocks.csv...")
stocks = pd.read_csv("data/stocks.csv")
stocks.to_sql("stocks", conn, if_exists="replace", index=False)
print(f"  Inserted {len(stocks):,} rows into stocks table.")

# Load enriched features
print("Loading stocks_features.csv...")
features = pd.read_csv("data/stocks_features.csv")
features.to_sql("stocks_features", conn, if_exists="replace", index=False)
print(f"  Inserted {len(features):,} rows into stocks_features table.")

conn.commit()

# Quick validation
print("\nDatabase validation:")
for view in ["v_latest_prices", "v_ticker_summary", "v_risk_metrics"]:
    result = pd.read_sql(f"SELECT * FROM {view}", conn)
    print(f"\n{view}:")
    print(result.to_string(index=False))

conn.close()
print(f"\nDatabase saved to {DB_PATH}")
