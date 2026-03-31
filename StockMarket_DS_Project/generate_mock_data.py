"""
generate_mock_data.py
---------------------
Generates 3 years of realistic daily OHLCV stock data for 5 tickers
using Geometric Brownian Motion (the industry-standard price simulation model).
Saves to CSV files in the data/ folder.
"""

import numpy as np
import pandas as pd
import os

os.makedirs("data", exist_ok=True)
np.random.seed(42)

# --- Config ---
TICKERS = {
    "AAPL":  {"start_price": 150.0, "mu": 0.0003, "sigma": 0.018},
    "MSFT":  {"start_price": 280.0, "mu": 0.0004, "sigma": 0.016},
    "GOOGL": {"start_price": 100.0, "mu": 0.0003, "sigma": 0.020},
    "AMZN":  {"start_price": 120.0, "mu": 0.0002, "sigma": 0.022},
    "TSLA":  {"start_price": 200.0, "mu": 0.0005, "sigma": 0.035},
}

START_DATE = "2022-01-03"
END_DATE   = "2024-12-31"

trading_days = pd.bdate_range(start=START_DATE, end=END_DATE)


def simulate_ohlcv(ticker, config, dates):
    """Simulate daily OHLCV data using Geometric Brownian Motion."""
    n = len(dates)
    mu    = config["mu"]
    sigma = config["sigma"]
    S0    = config["start_price"]

    # Daily log returns
    daily_returns = np.random.normal(mu - 0.5 * sigma**2, sigma, n)
    prices = S0 * np.exp(np.cumsum(daily_returns))

    # Intraday range: high/low around close
    intraday_range = np.abs(np.random.normal(0, sigma * 1.5, n)) * prices
    high  = prices + intraday_range * np.random.uniform(0.3, 0.7, n)
    low   = prices - intraday_range * np.random.uniform(0.3, 0.7, n)
    open_ = low + (high - low) * np.random.uniform(0.2, 0.8, n)
    low   = np.minimum(low, np.minimum(open_, prices))
    high  = np.maximum(high, np.maximum(open_, prices))

    # Volume: higher on volatile days
    base_volume   = np.random.randint(20_000_000, 80_000_000)
    volume_factor = 1 + 5 * np.abs(daily_returns / sigma)
    volume        = (base_volume * volume_factor * np.random.uniform(0.8, 1.2, n)).astype(int)

    df = pd.DataFrame({
        "date":   dates,
        "ticker": ticker,
        "open":   open_.round(2),
        "high":   high.round(2),
        "low":    low.round(2),
        "close":  prices.round(2),
        "volume": volume,
    })
    return df


# --- Generate all tickers ---
all_data = []
for ticker, config in TICKERS.items():
    print(f"Generating data for {ticker}...")
    df = simulate_ohlcv(ticker, config, trading_days)
    all_data.append(df)

stocks_df = pd.concat(all_data, ignore_index=True)
stocks_df.to_csv("data/stocks.csv", index=False)
print(f"\nSaved {len(stocks_df):,} rows to data/stocks.csv")
print(stocks_df.groupby("ticker")[["close"]].agg(["min", "max", "mean"]).round(2))
