-- ============================================================
-- Stock Market Analytics — SQLite Schema
-- ============================================================

-- Raw daily OHLCV prices
CREATE TABLE IF NOT EXISTS stocks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    date        DATE         NOT NULL,
    ticker      VARCHAR(10)  NOT NULL,
    open        NUMERIC(10,2),
    high        NUMERIC(10,2),
    low         NUMERIC(10,2),
    close       NUMERIC(10,2),
    volume      BIGINT,
    UNIQUE(date, ticker)
);

-- Enriched dataset with technical indicators
CREATE TABLE IF NOT EXISTS stocks_features (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    date             DATE        NOT NULL,
    ticker           VARCHAR(10) NOT NULL,
    close            NUMERIC(10,4),
    sma_5            NUMERIC(10,4),
    sma_20           NUMERIC(10,4),
    sma_50           NUMERIC(10,4),
    ema_12           NUMERIC(10,4),
    ema_26           NUMERIC(10,4),
    macd             NUMERIC(10,4),
    macd_signal      NUMERIC(10,4),
    macd_hist        NUMERIC(10,4),
    rsi_14           NUMERIC(10,4),
    bb_upper         NUMERIC(10,4),
    bb_lower         NUMERIC(10,4),
    bb_width         NUMERIC(10,4),
    bb_position      NUMERIC(10,4),
    daily_return     NUMERIC(10,6),
    return_5d        NUMERIC(10,6),
    return_20d       NUMERIC(10,6),
    log_return       NUMERIC(10,6),
    volatility_20d   NUMERIC(10,6),
    volume_ma_20     NUMERIC(20,2),
    volume_ratio     NUMERIC(10,4),
    high_low_range   NUMERIC(10,6),
    price_vs_sma20   NUMERIC(10,6),
    target           INTEGER,
    UNIQUE(date, ticker)
);

-- Useful views

-- Latest price snapshot per ticker
CREATE VIEW IF NOT EXISTS v_latest_prices AS
SELECT
    ticker,
    MAX(date)  AS last_date,
    close      AS last_close
FROM stocks
GROUP BY ticker;

-- Summary statistics per ticker
CREATE VIEW IF NOT EXISTS v_ticker_summary AS
SELECT
    ticker,
    COUNT(*)           AS trading_days,
    MIN(close)         AS min_price,
    MAX(close)         AS max_price,
    ROUND(AVG(close),2)AS avg_price,
    MIN(date)          AS start_date,
    MAX(date)          AS end_date
FROM stocks
GROUP BY ticker;

-- Average RSI and volatility per ticker
CREATE VIEW IF NOT EXISTS v_risk_metrics AS
SELECT
    ticker,
    ROUND(AVG(rsi_14), 2)        AS avg_rsi,
    ROUND(AVG(volatility_20d), 4) AS avg_volatility,
    ROUND(AVG(daily_return), 6)   AS avg_daily_return,
    ROUND(AVG(volume_ratio), 4)   AS avg_volume_ratio
FROM stocks_features
GROUP BY ticker;
