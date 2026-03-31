import numpy as np
import pandas as pd
import os
os.makedirs("data", exist_ok=True)

np.random.seed(42)


# --- basic config ---
turbines = [f"T{i:02d}" for i in range(1, 6)]
rated_power_kw = 3000
start = "2023-01-01"
end = "2023-12-31 23:50"
freq = "10min"

ts_index = pd.date_range(start=start, end=end, freq=freq)

# --- helper: simple power curve ---


def power_curve(wind_ms):
    # cut-in, rated, cut-out
    cut_in, rated, cut_out = 3, 12, 25
    power = np.zeros_like(wind_ms)
    # below cut-in: 0
    mask_mid = (wind_ms >= cut_in) & (wind_ms < rated)
    power[mask_mid] = rated_power_kw * \
        ((wind_ms[mask_mid] - cut_in) / (rated - cut_in)) ** 3
    mask_rated = (wind_ms >= rated) & (wind_ms <= cut_out)
    power[mask_rated] = rated_power_kw
    # above cut-out: 0
    return power


# --- weather (site-level) ---
weather = pd.DataFrame(index=ts_index)
# diurnal + seasonal wind pattern
hours = weather.index.hour
day_factor = 1 + 0.3 * np.sin(2 * np.pi * (hours - 6) / 24)
day_of_year = weather.index.dayofyear
season_factor = 1 + 0.2 * np.sin(2 * np.pi * (day_of_year - 80) / 365)

base_wind = 7  # m/s
weather["wind_speed_ms"] = base_wind * day_factor * \
    season_factor + np.random.normal(0, 1.5, len(weather))
weather["wind_speed_ms"] = weather["wind_speed_ms"].clip(lower=0)

weather["wind_direction_deg"] = (180 + 40 * np.sin(2 * np.pi * day_of_year / 365)
                                 + np.random.normal(0, 20, len(weather))) % 360
weather["temperature_c"] = 10 + 10 * np.sin(2 * np.pi * (day_of_year - 170) / 365) \
    + np.random.normal(0, 2, len(weather))
weather["pressure_hpa"] = 1013 + np.random.normal(0, 5, len(weather))
weather["precip_mm"] = np.random.choice([0, 0, 0, 0.5, 1.0, 2.0], size=len(
    weather), p=[0.7, 0.1, 0.05, 0.1, 0.03, 0.02])
weather["icing_flag"] = ((weather["temperature_c"] < 0) & (
    weather["precip_mm"] > 0.5)).astype(bool)

weather.reset_index(names="ts", inplace=True)

# --- telemetry per turbine ---
telemetry_list = []
yield_list = []
downtime_list = []

for t in turbines:
    df_t = weather.copy()
    df_t["turbine_id"] = t

    # turbine-specific wind variation
    df_t["wind_speed_ms"] = df_t["wind_speed_ms"] + \
        np.random.normal(0, 0.5, len(df_t))

    # base power from power curve
    wind = df_t["wind_speed_ms"].to_numpy()
    power = power_curve(wind)

    # add noise and some random curtailment
    noise = np.random.normal(0, rated_power_kw * 0.05, len(df_t))
    curtailment_factor = np.where(np.random.rand(len(df_t)) < 0.02, 0.5, 1.0)
    df_t["power_kw"] = (power * curtailment_factor + noise).clip(min=0)

    # rotor speed roughly proportional to wind
    df_t["rotor_speed_rpm"] = 5 * wind + np.random.normal(0, 2, len(df_t))
    df_t["rotor_speed_rpm"] = df_t["rotor_speed_rpm"].clip(lower=0)

    # energy yield: power * (10/60) hours
    df_t["energy_kwh"] = df_t["power_kw"] * (10 / 60)

    # --- downtime events (random + weather-related) ---
    # create a downtime flag series
    downtime_flag = np.zeros(len(df_t), dtype=bool)

    # random maintenance events
    n_events = 20
    event_indices = np.random.choice(len(df_t), size=n_events, replace=False)
    for idx in event_indices:
        length = np.random.randint(3, 24)  # 3–24 intervals (30 min–4 hours)
        downtime_flag[idx:idx+length] = True

    # high wind shutdowns
    high_wind = df_t["wind_speed_ms"] > 22
    downtime_flag = downtime_flag | high_wind.to_numpy()

    # icing-related downtime
    icing = df_t["icing_flag"].to_numpy()
    icing_events = np.where(icing & (np.random.rand(len(df_t)) < 0.3))[0]
    for idx in icing_events:
        length = np.random.randint(3, 12)
        downtime_flag[idx:idx+length] = True

    df_t["is_downtime"] = downtime_flag

    # zero power during downtime
    df_t.loc[df_t["is_downtime"], "power_kw"] = 0
    df_t.loc[df_t["is_downtime"], "energy_kwh"] = 0

    # build downtime table from flag
    in_event = False
    start_idx = None
    for i, flag in enumerate(downtime_flag):
        if flag and not in_event:
            in_event = True
            start_idx = i
        elif not flag and in_event:
            in_event = False
            end_idx = i
            event = {
                "turbine_id": t,
                "event_start": df_t.loc[start_idx, "ts"],
                "event_end": df_t.loc[end_idx - 1, "ts"],
                "event_type": np.random.choice(["Maintenance", "High wind", "Icing"]),
                "cause": np.random.choice(["Scheduled", "Unscheduled", "Weather"]),
                "severity": np.random.choice(["Low", "Medium", "High"])
            }
            downtime_list.append(event)
    # handle event running to end
    if in_event:
        event = {
            "turbine_id": t,
            "event_start": df_t.loc[start_idx, "ts"],
            "event_end": df_t.loc[len(df_t) - 1, "ts"],
            "event_type": np.random.choice(["Maintenance", "High wind", "Icing"]),
            "cause": np.random.choice(["Scheduled", "Unscheduled", "Weather"]),
            "severity": np.random.choice(["Low", "Medium", "High"])
        }
        downtime_list.append(event)

    telemetry_list.append(df_t[["turbine_id", "ts", "power_kw", "rotor_speed_rpm",
                                "wind_speed_ms", "wind_direction_deg"]])
    yield_list.append(df_t[["turbine_id", "ts", "energy_kwh"]])

telemetry = pd.concat(telemetry_list, ignore_index=True)
energy_yield = pd.concat(yield_list, ignore_index=True)
downtime = pd.DataFrame(downtime_list)

# --- save to CSV ---
weather.to_csv("data/weather.csv", index=False)
telemetry.to_csv("data/telemetry.csv", index=False)
energy_yield.to_csv("data/yield.csv", index=False)
downtime.to_csv("data/downtime.csv", index=False)

# turbines table
turbines_df = pd.DataFrame({
    "turbine_id": turbines,
    "rated_power_kw": rated_power_kw,
    "hub_height_m": 100,
    "model": "WT-3MW"
})
turbines_df.to_csv("data/turbines.csv", index=False)
