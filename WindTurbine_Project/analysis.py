from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import pandas as pd
import numpy as np
import sqlalchemy as sa
import matplotlib.pyplot as plt
import seaborn as sns
import os
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()

DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "wind_turbine")

# --- MySQL connection ---
engine = sa.create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Load unified hourly dataset
df = pd.read_sql("SELECT * FROM v_turbine_hourly",
                 engine, parse_dates=["ts_hour"])

df = df.sort_values(["turbine_id", "ts_hour"])
print(df.head())

# Time series analysis

# Set index for resampling
df_ts = df.set_index("ts_hour")

# Daily energy per turbine
daily_energy = (
    df_ts.groupby("turbine_id")["energy_kwh"]
         .resample("D")
         .sum()
         .reset_index()
)

plt.figure(figsize=(12, 5))
sns.lineplot(data=daily_energy, x="ts_hour", y="energy_kwh", hue="turbine_id")
plt.title("Daily Energy Yield per Turbine")
plt.tight_layout()
plt.show()


# Capacity Factor
rated_power_kw = 3000
df["capacity_factor"] = df["avg_power_kw"] / rated_power_kw

monthly_cf = (
    df.set_index("ts_hour")
      .groupby("turbine_id")["capacity_factor"]
      .resample("M")
      .mean()
      .reset_index()
)

plt.figure(figsize=(10, 4))
sns.lineplot(data=monthly_cf, x="ts_hour",
             y="capacity_factor", hue="turbine_id")
plt.title("Monthly Capacity Factor")
plt.tight_layout()
plt.show()


# Power Curve (Wind Speed → Power)

df["wind_bin"] = pd.cut(df["wind_ms"], bins=np.arange(0, 30, 1))
power_curve = df.groupby("wind_bin")["avg_power_kw"].mean()

plt.figure(figsize=(12, 4))
power_curve.plot(kind="bar")
plt.title("Empirical Power Curve")
plt.ylabel("Power (kW)")
plt.tight_layout()
plt.show()


# Downtime & Lost Energy Estimation

# Expected power = rolling median (baseline)
df["expected_power_kw"] = (
    df.groupby("turbine_id")["avg_power_kw"]
      .transform(lambda x: x.rolling(48, min_periods=1).median())
)

# Lost energy = expected - actual
df["lost_energy_kwh"] = (df["expected_power_kw"] -
                         df["avg_power_kw"]).clip(lower=0)

lost_energy = df.groupby("turbine_id")["lost_energy_kwh"].sum()
print("Lost energy (kWh):")
print(lost_energy)


# Weather Impact Analysis

# Correlation matrix
corr = df[["avg_power_kw", "wind_ms", "temp_c", "icing_flag"]].corr()
sns.heatmap(corr, annot=True, cmap="coolwarm")
plt.title("Weather → Power Correlation")
plt.show()


# Downtime probability by weather

print(df.groupby("icing_flag")["is_downtime"].mean())
print(df.groupby(pd.cut(df["wind_ms"], bins=[0, 10, 20, 30]))[
      "is_downtime"].mean())


# Machine Learning Models

# A. Predict Power Output (Regression)


X = df[["wind_ms", "temp_c", "icing_flag"]]
y = df["avg_power_kw"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestRegressor(n_estimators=300)
model.fit(X_train, y_train)

print("R² Score:", model.score(X_test, y_test))


# B.Predict Downtime (Classification)


clf = LogisticRegression(max_iter=1000)
clf.fit(X_train, df.loc[X_train.index, "is_downtime"])

print("Downtime prediction accuracy:", clf.score(
    X_test, df.loc[X_test.index, "is_downtime"]))
