"""
feature_engineering.py
-----------------------
Loads raw stock data, calculates professional technical indicators,
and saves an enriched dataset ready for EDA and ML modeling.

Technical indicators calculated:
  - Simple Moving Averages (SMA 5, 20, 50)
  - Exponential Moving Averages (EMA 12, 26)
  - MACD & Signal Line
  - Relative Strength Index (RSI 14)
  - Bollinger Bands (upper, lower, width)
  - Daily & 5-day returns
  - Volume moving average
  - Target variable: next-day price direction (1=up, 0=down)
"""

import pandas as pd
import numpy as np


def compute_rsi(series, period=14):
    delta = series.diff()
    gain  = delta.clip(lower=0)
    loss  = -delta.clip(upper=0)
    avg_gain = gain.ewm(com=period - 1, min_periods=period).mean()
    avg_loss = loss.ewm(com=period - 1, min_periods=period).mean()
    rs  = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi


def compute_bollinger_bands(series, window=20, num_std=2):
    sma    = series.rolling(window).mean()
    std    = series.rolling(window).std()
    upper  = sma + num_std * std
    lower  = sma - num_std * std
    width  = (upper - lower) / sma
    return upper, lower, width


def add_features(df):
    """Add all technical indicators to a single-ticker dataframe."""
    df = df.sort_values("date").copy()
    close  = df["close"]
    volume = df["volume"]

    # --- Moving Averages ---
    df["sma_5"]  = close.rolling(5).mean()
    df["sma_20"] = close.rolling(20).mean()
    df["sma_50"] = close.rolling(50).mean()
    df["ema_12"] = close.ewm(span=12, adjust=False).mean()
    df["ema_26"] = close.ewm(span=26, adjust=False).mean()

    # --- MACD ---
    df["macd"]        = df["ema_12"] - df["ema_26"]
    df["macd_signal"] = df["macd"].ewm(span=9, adjust=False).mean()
    df["macd_hist"]   = df["macd"] - df["macd_signal"]

    # --- RSI ---
    df["rsi_14"] = compute_rsi(close, 14)

    # --- Bollinger Bands ---
    df["bb_upper"], df["bb_lower"], df["bb_width"] = compute_bollinger_bands(close)
    df["bb_position"] = (close - df["bb_lower"]) / (df["bb_upper"] - df["bb_lower"])

    # --- Returns ---
    df["daily_return"]  = close.pct_change()
    df["return_5d"]     = close.pct_change(5)
    df["return_20d"]    = close.pct_change(20)
    df["log_return"]    = np.log(close / close.shift(1))

    # --- Volatility ---
    df["volatility_20d"] = df["log_return"].rolling(20).std() * np.sqrt(252)

    # --- Volume ---
    df["volume_ma_20"]   = volume.rolling(20).mean()
    df["volume_ratio"]   = volume / df["volume_ma_20"]

    # --- Price position ---
    df["high_low_range"] = (df["high"] - df["low"]) / close
    df["price_vs_sma20"] = (close - df["sma_20"]) / df["sma_20"]

    # --- Target: next-day direction ---
    df["target"] = (close.shift(-1) > close).astype(int)

    return df


# --- Main ---
print("Loading raw stock data...")
stocks = pd.read_csv("data/stocks.csv", parse_dates=["date"])

print("Computing technical indicators for each ticker...")
enriched_frames = []
for ticker, group in stocks.groupby("ticker"):
    print(f"  Processing {ticker}...")
    enriched = add_features(group)
    enriched_frames.append(enriched)

enriched_df = pd.concat(enriched_frames, ignore_index=True)

# Drop rows with NaN (from rolling windows)
enriched_df.dropna(inplace=True)

enriched_df.to_csv("data/stocks_features.csv", index=False)
print(f"\nSaved {len(enriched_df):,} rows to data/stocks_features.csv")
print(f"Features: {list(enriched_df.columns)}")
print(f"\nTarget distribution:\n{enriched_df['target'].value_counts(normalize=True).round(3)}")
