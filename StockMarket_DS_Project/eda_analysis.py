"""
eda_analysis.py
---------------
Exploratory Data Analysis for the stock market dataset.
Produces 6 professional charts saved to the charts/ folder.

Charts:
  1. Price history for all tickers
  2. Candlestick-style chart (AAPL)
  3. Correlation heatmap of features
  4. Return distribution per ticker
  5. RSI over time (AAPL)
  6. Bollinger Bands (AAPL)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import os

os.makedirs("charts", exist_ok=True)

# --- Style ---
plt.rcParams.update({
    "figure.facecolor": "#0d1117",
    "axes.facecolor":   "#161b22",
    "axes.edgecolor":   "#30363d",
    "axes.labelcolor":  "#c9d1d9",
    "text.color":       "#c9d1d9",
    "xtick.color":      "#8b949e",
    "ytick.color":      "#8b949e",
    "grid.color":       "#21262d",
    "grid.linestyle":   "--",
    "grid.alpha":       0.5,
    "font.family":      "DejaVu Sans",
})

COLORS = ["#58a6ff", "#3fb950", "#f78166", "#d2a8ff", "#ffa657"]

print("Loading data...")
df = pd.read_csv("data/stocks_features.csv", parse_dates=["date"])
tickers = df["ticker"].unique()

# ─────────────────────────────────────────────
# Chart 1: Normalized Price History
# ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6))
for i, ticker in enumerate(tickers):
    sub = df[df["ticker"] == ticker].sort_values("date")
    normalized = sub["close"] / sub["close"].iloc[0] * 100
    ax.plot(sub["date"], normalized, label=ticker, color=COLORS[i], linewidth=1.5)

ax.set_title("Normalized Price Performance (Base = 100)", fontsize=14, pad=15)
ax.set_ylabel("Indexed Price")
ax.set_xlabel("Date")
ax.legend(loc="upper left")
ax.grid(True)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
plt.tight_layout()
plt.savefig("charts/01_price_history.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved charts/01_price_history.png")

# ─────────────────────────────────────────────
# Chart 2: Candlestick (AAPL - last 60 days)
# ─────────────────────────────────────────────
aapl = df[df["ticker"] == "AAPL"].sort_values("date").tail(60).reset_index(drop=True)

fig, ax = plt.subplots(figsize=(14, 5))
for i, row in aapl.iterrows():
    color = "#3fb950" if row["close"] >= row["open"] else "#f78166"
    ax.plot([i, i], [row["low"], row["high"]], color=color, linewidth=1)
    ax.bar(i, abs(row["close"] - row["open"]),
           bottom=min(row["open"], row["close"]),
           color=color, width=0.6)

step = max(1, len(aapl) // 8)
ax.set_xticks(range(0, len(aapl), step))
ax.set_xticklabels(
    aapl["date"].iloc[::step].dt.strftime("%b %d"),
    rotation=30, ha="right"
)
ax.set_title("AAPL — Candlestick Chart (Last 60 Trading Days)", fontsize=14, pad=15)
ax.set_ylabel("Price (USD)")
ax.grid(True, axis="y")
plt.tight_layout()
plt.savefig("charts/02_candlestick_aapl.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved charts/02_candlestick_aapl.png")

# ─────────────────────────────────────────────
# Chart 3: Feature Correlation Heatmap
# ─────────────────────────────────────────────
feature_cols = [
    "daily_return", "return_5d", "rsi_14", "macd", "macd_hist",
    "bb_width", "bb_position", "volatility_20d", "volume_ratio",
    "price_vs_sma20", "high_low_range", "target"
]
corr = df[feature_cols].corr()

fig, ax = plt.subplots(figsize=(12, 10))
sns.heatmap(
    corr, annot=True, fmt=".2f", cmap="coolwarm",
    center=0, linewidths=0.5, ax=ax,
    annot_kws={"size": 8}
)
ax.set_title("Feature Correlation Matrix", fontsize=14, pad=15)
plt.tight_layout()
plt.savefig("charts/03_correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved charts/03_correlation_heatmap.png")

# ─────────────────────────────────────────────
# Chart 4: Return Distribution
# ─────────────────────────────────────────────
fig, axes = plt.subplots(1, len(tickers), figsize=(16, 4), sharey=True)
for i, ticker in enumerate(tickers):
    sub = df[df["ticker"] == ticker]["daily_return"] * 100
    axes[i].hist(sub, bins=60, color=COLORS[i], alpha=0.85, edgecolor="none")
    axes[i].axvline(sub.mean(), color="white", linestyle="--", linewidth=1)
    axes[i].set_title(ticker, fontsize=11)
    axes[i].set_xlabel("Daily Return (%)")
    if i == 0:
        axes[i].set_ylabel("Frequency")
    axes[i].grid(True, axis="y")

fig.suptitle("Daily Return Distribution by Ticker", fontsize=14, y=1.02)
plt.tight_layout()
plt.savefig("charts/04_return_distributions.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved charts/04_return_distributions.png")

# ─────────────────────────────────────────────
# Chart 5: RSI Over Time (AAPL)
# ─────────────────────────────────────────────
aapl_full = df[df["ticker"] == "AAPL"].sort_values("date")

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 7), sharex=True, gridspec_kw={"height_ratios": [2, 1]})

ax1.plot(aapl_full["date"], aapl_full["close"], color="#58a6ff", linewidth=1.2)
ax1.set_title("AAPL — Price & RSI(14)", fontsize=14, pad=15)
ax1.set_ylabel("Price (USD)")
ax1.grid(True)

ax2.plot(aapl_full["date"], aapl_full["rsi_14"], color="#d2a8ff", linewidth=1)
ax2.axhline(70, color="#f78166", linestyle="--", linewidth=0.8, label="Overbought (70)")
ax2.axhline(30, color="#3fb950", linestyle="--", linewidth=0.8, label="Oversold (30)")
ax2.fill_between(aapl_full["date"], aapl_full["rsi_14"], 70,
                 where=(aapl_full["rsi_14"] >= 70), alpha=0.3, color="#f78166")
ax2.fill_between(aapl_full["date"], aapl_full["rsi_14"], 30,
                 where=(aapl_full["rsi_14"] <= 30), alpha=0.3, color="#3fb950")
ax2.set_ylabel("RSI")
ax2.set_ylim(0, 100)
ax2.legend(loc="upper right", fontsize=8)
ax2.grid(True)
ax2.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

plt.tight_layout()
plt.savefig("charts/05_rsi_aapl.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved charts/05_rsi_aapl.png")

# ─────────────────────────────────────────────
# Chart 6: Bollinger Bands (AAPL)
# ─────────────────────────────────────────────
aapl_bb = aapl_full.tail(250)

fig, ax = plt.subplots(figsize=(14, 5))
ax.plot(aapl_bb["date"], aapl_bb["close"],   color="#58a6ff", linewidth=1.5, label="Close")
ax.plot(aapl_bb["date"], aapl_bb["sma_20"],  color="#ffa657", linewidth=1, linestyle="--", label="SMA 20")
ax.plot(aapl_bb["date"], aapl_bb["bb_upper"],color="#f78166", linewidth=0.8, label="Upper Band")
ax.plot(aapl_bb["date"], aapl_bb["bb_lower"],color="#3fb950", linewidth=0.8, label="Lower Band")
ax.fill_between(aapl_bb["date"], aapl_bb["bb_upper"], aapl_bb["bb_lower"],
                alpha=0.1, color="#58a6ff")
ax.set_title("AAPL — Bollinger Bands (Last 250 Trading Days)", fontsize=14, pad=15)
ax.set_ylabel("Price (USD)")
ax.legend(loc="upper left")
ax.grid(True)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))

plt.tight_layout()
plt.savefig("charts/06_bollinger_bands_aapl.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved charts/06_bollinger_bands_aapl.png")

print("\nAll charts saved to charts/ folder.")
