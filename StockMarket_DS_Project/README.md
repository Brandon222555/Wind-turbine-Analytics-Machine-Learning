# Stock Market Analytics & Prediction System

A full end-to-end data science project that simulates stock market data, engineers professional financial features, performs exploratory analysis, and applies machine learning to predict next-day price direction.

Built to demonstrate real-world data science skills for hiring managers — covering the complete pipeline from raw data to ML model evaluation.

---

## Skills Demonstrated

- **Data Engineering** — Realistic stock simulation using Geometric Brownian Motion
- **Feature Engineering** — 16 technical indicators (RSI, MACD, Bollinger Bands, etc.)
- **SQL & Databases** — SQLite schema with views and structured queries
- **Exploratory Data Analysis** — 6 professional charts including candlesticks and heatmaps
- **Machine Learning** — 4 models compared with time-series cross-validation
- **Model Evaluation** — ROC curves, confusion matrices, feature importance

---

## Project Structure

```
StockMarket_DS_Project/
│
├── generate_mock_data.py     # Simulate 3 years of OHLCV data for 5 tickers
├── feature_engineering.py    # Calculate 16 technical indicators + target variable
├── load_to_db.py             # Load data into SQLite database
├── eda_analysis.py           # Exploratory data analysis — 6 charts
├── ml_models.py              # Train & compare 4 ML models — 4 charts
├── schema.sql                # SQLite database schema and views
│
├── data/                     # Generated CSV + database files (git-ignored)
│   ├── stocks.csv
│   ├── stocks_features.csv
│   └── stocks.db
│
├── charts/                   # Output charts (git-ignored)
│   ├── 01_price_history.png
│   ├── 02_candlestick_aapl.png
│   ├── 03_correlation_heatmap.png
│   ├── 04_return_distributions.png
│   ├── 05_rsi_aapl.png
│   ├── 06_bollinger_bands_aapl.png
│   ├── 07_roc_curves.png
│   ├── 08_feature_importance.png
│   ├── 09_confusion_matrices.png
│   └── 10_model_comparison.png
│
├── .gitignore
└── README.md
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Brandon222555/Python-projects.git
cd Python-projects/StockMarket_DS_Project
```

### 2. Install dependencies

```bash
pip install pandas numpy matplotlib seaborn scikit-learn
```

No database server needed — SQLite is built into Python.

### 3. Run the full pipeline in order

```bash
python generate_mock_data.py      # Step 1 — Generate raw stock data
python feature_engineering.py     # Step 2 — Add technical indicators
python load_to_db.py              # Step 3 — Load into SQLite
python eda_analysis.py            # Step 4 — Generate EDA charts
python ml_models.py               # Step 5 — Train & evaluate ML models
```

---

## Dataset

| Detail | Value |
|--------|-------|
| Tickers | AAPL, MSFT, GOOGL, AMZN, TSLA (simulated) |
| Period | Jan 2022 — Dec 2024 |
| Frequency | Daily (trading days only) |
| Rows | ~3,770 (754 days × 5 tickers) |
| Features | 16 technical indicators |
| Target | Next-day price direction (1=up, 0=down) |

---

## Technical Indicators

| Indicator | Description |
|-----------|-------------|
| SMA 5/20/50 | Simple moving averages |
| EMA 12/26 | Exponential moving averages |
| MACD | Momentum trend indicator |
| RSI 14 | Overbought/oversold signal (0–100) |
| Bollinger Bands | Volatility envelope around price |
| Daily/5d/20d Return | Price change over multiple windows |
| Volatility (20d) | Annualized rolling standard deviation |
| Volume Ratio | Volume vs. 20-day average |

---

## ML Models Compared

| Model | Notes |
|-------|-------|
| Logistic Regression | Baseline — interpretable |
| Random Forest | Ensemble, handles nonlinearity |
| Gradient Boosting | High accuracy, sequential learner |
| Support Vector Machine | Kernel-based margin classifier |

All models evaluated using **time-series cross-validation** (no lookahead bias) and compared on Test Accuracy and ROC-AUC.

---

## Dependencies

- `pandas`, `numpy` — Data manipulation
- `matplotlib`, `seaborn` — Visualization
- `scikit-learn` — Machine learning models and evaluation
- `sqlite3` — Database (built into Python)
