--


CREATE TABLE turbines (
    turbine_id      VARCHAR(10) PRIMARY KEY,
    rated_power_kw  NUMERIC(10,2),
    hub_height_m    NUMERIC(10,2),
    model           VARCHAR(50)
);

CREATE TABLE telemetry (
    turbine_id          VARCHAR(10) REFERENCES turbines(turbine_id),
    ts                  DATETIME , # without time zone
    power_kw            NUMERIC(10,2),
    rotor_speed_rpm     NUMERIC(10,2),
    wind_speed_ms       NUMERIC(10,2),
    wind_direction_deg  NUMERIC(10,2),
    PRIMARY KEY (turbine_id, ts)
);

CREATE TABLE energy_yield (
    turbine_id  VARCHAR(10) REFERENCES turbines(turbine_id),
    ts          DATETIME,	# without time zone
    energy_kwh  NUMERIC(10,2),
    PRIMARY KEY (turbine_id, ts)
);

CREATE TABLE weather (
    ts              DATETIME PRIMARY KEY, 	# without time zone
    wind_speed_ms   NUMERIC(10,2),
    wind_direction_deg NUMERIC(10,2),
    temperature_c   NUMERIC(10,2),
    pressure_hpa    NUMERIC(10,2),
    precip_mm       NUMERIC(10,2),
    icing_flag      BOOLEAN
);

CREATE TABLE downtime (
    downtime_id SERIAL PRIMARY KEY,
    turbine_id  VARCHAR(10) REFERENCES turbines(turbine_id),
    event_start DATETIME,		# without time zone
    event_end   DATETIME,      # without time zone
    event_type  VARCHAR(50),
    cause       VARCHAR(100),
    severity    VARCHAR(20)
);


-- hourly telemetry
CREATE VIEW v_hourly_telemetry AS
SELECT
    t.turbine_id,
    DATE_TRUNC('hour', t.ts) AS ts_hour,
    AVG(t.power_kw) AS avg_power_kw,
    AVG(t.rotor_speed_rpm) AS avg_rotor_rpm,
    AVG(t.wind_speed_ms) AS avg_wind_ms,
    AVG(t.wind_direction_deg) AS avg_wind_dir
FROM telemetry t
GROUP BY t.turbine_id, DATE_TRUNC('hour', t.ts);

-- hourly yield 
CREATE VIEW v_hourly_yield AS
SELECT
    y.turbine_id,
    DATE_TRUNC('hour', y.ts) AS ts_hour,
    SUM(y.energy_kwh) AS energy_kwh
FROM energy_yield y
GROUP BY y.turbine_id, DATE_TRUNC('hour', y.ts);

-- hourly weather
CREATE VIEW v_hourly_weather AS
SELECT
    DATE_TRUNC('hour', w.ts) AS ts_hour,
    AVG(w.wind_speed_ms) AS wind_ms,
    AVG(w.wind_direction_deg) AS wind_dir_deg,
    AVG(w.temperature_c) AS temp_c,
    AVG(w.pressure_hpa) AS pressure_hpa,
    SUM(w.precip_mm) AS precip_mm,
    BOOL_OR(w.icing_flag) AS icing_flag
FROM weather w
GROUP BY DATE_TRUNC('hour', w.ts);


-- hourly downtime flags

CREATE VIEW v_hourly_downtime AS

WITH RECURSIVE hours AS (
    SELECT 
        MIN(ts) AS ts_hour
    FROM telemetry

    UNION ALL

    SELECT 
        DATE_ADD(ts_hour, INTERVAL 1 HOUR)
    FROM hours
    WHERE ts_hour < (SELECT MAX(ts) FROM telemetry)
),


turbine_hours AS (
    SELECT 
        t.turbine_id,
        h.ts_hour
    FROM (SELECT DISTINCT turbine_id FROM telemetry) t
    CROSS JOIN hours h
),
downtime_expanded AS (
    SELECT
        d.turbine_id,
        h.ts_hour
    FROM downtime d
    JOIN hours h
      ON h.ts_hour >= DATE_FORMAT(d.event_start, '%Y-%m-%d %H:00:00')
     AND h.ts_hour <  DATE_FORMAT(d.event_end, '%Y-%m-%d %H:00:00')
)
SELECT
    th.turbine_id,
    th.ts_hour,
    CASE WHEN de.turbine_id IS NOT NULL THEN 1 ELSE 0 END AS is_downtime
FROM turbine_hours th
LEFT JOIN downtime_expanded de
  ON th.turbine_id = de.turbine_id
 AND th.ts_hour = de.ts_hour;


-- master table

-- Hourly Telemetry View
CREATE OR REPLACE VIEW v_hourly_telemetry AS
SELECT
    turbine_id,
    DATE_FORMAT(ts, '%Y-%m-%d %H:00:00') AS ts_hour,
    AVG(power_kw) AS avg_power_kw,
    AVG(rotor_speed_rpm) AS avg_rotor_rpm,
    AVG(wind_speed_ms) AS avg_wind_ms,
    AVG(wind_direction_deg) AS avg_wind_dir
FROM telemetry
GROUP BY turbine_id, DATE_FORMAT(ts, '%Y-%m-%d %H:00:00');

-- Hourly Yield View
CREATE OR REPLACE VIEW v_hourly_yield AS
SELECT
    turbine_id,
    DATE_FORMAT(ts, '%Y-%m-%d %H:00:00') AS ts_hour,
    SUM(energy_kwh) AS energy_kwh
FROM energy_yield
GROUP BY turbine_id, DATE_FORMAT(ts, '%Y-%m-%d %H:00:00');


-- Hourly Weather View

CREATE OR REPLACE VIEW v_hourly_weather AS
SELECT
    DATE_FORMAT(ts, '%Y-%m-%d %H:00:00') AS ts_hour,
    AVG(wind_speed_ms) AS wind_ms,
    AVG(wind_direction_deg) AS wind_dir_deg,
    AVG(temperature_c) AS temp_c,
    AVG(pressure_hpa) AS pressure_hpa,
    SUM(precip_mm) AS precip_mm,
    MAX(icing_flag) AS icing_flag
FROM weather
GROUP BY DATE_FORMAT(ts, '%Y-%m-%d %H:00:00');
DROP VIEW v_hourly_downtime;
-- Hourly Downtime View (MySQL Recursive CTE)

CREATE OR REPLACE VIEW v_hourly_downtime AS
WITH RECURSIVE hours AS (
    SELECT 
        (SELECT MIN(ts) FROM telemetry) AS ts_hour,
        0 AS depth
    UNION ALL
    SELECT 
        DATE_ADD(ts_hour, INTERVAL 1 HOUR),
        depth + 1
    FROM hours
    WHERE ts_hour < (SELECT MAX(ts) FROM telemetry)
      AND depth < 20000   -- safety limit
),
turbine_hours AS (
    SELECT t.turbine_id, h.ts_hour
    FROM (SELECT DISTINCT turbine_id FROM telemetry) t
    CROSS JOIN hours h
),
downtime_expanded AS (
    SELECT
        d.turbine_id,
        h.ts_hour
    FROM downtime d
    JOIN hours h
      ON h.ts_hour >= DATE_FORMAT(d.event_start, '%Y-%m-%d %H:00:00')
     AND h.ts_hour <  DATE_FORMAT(d.event_end, '%Y-%m-%d %H:00:00')
)
SELECT
    th.turbine_id,
    th.ts_hour,
    CASE WHEN de.turbine_id IS NOT NULL THEN 1 ELSE 0 END AS is_downtime
FROM turbine_hours th
LEFT JOIN downtime_expanded de
  ON th.turbine_id = de.turbine_id
 AND th.ts_hour = de.ts_hour;


-- Master view

CREATE OR REPLACE VIEW v_turbine_hourly AS
SELECT
    ht.turbine_id,
    ht.ts_hour,
    ht.avg_power_kw,
    hy.energy_kwh,
    hw.wind_ms,
    hw.temp_c,
    hw.icing_flag,
    hd.is_downtime                                       
FROM v_hourly_telemetry ht
LEFT JOIN v_hourly_yield hy
  ON ht.turbine_id = hy.turbine_id
 AND ht.ts_hour = hy.ts_hour
LEFT JOIN v_hourly_weather hw
  ON ht.ts_hour = hw.ts_hour
LEFT JOIN v_hourly_downtime hd
  ON ht.turbine_id = hd.turbine_id
 AND ht.ts_hour = hd.ts_hour;

SELECT * FROM v_turbine_hourly LIMIT 100;






SELECT * 
FROM v_turbine_hourly;

SELECT * 
FROM telemetry;

SELECT * 
FROM energy_yield;

SELECT * 
FROM weather;

SELECT *
FROM downtime;

SELECT * 
FROM v_hourly_telemetry;

SELECT * 
FROM v_hourly_yield;

SELECT *
FROM v_hourly_weather;

SELECT * 
FROM v_hourly_downtime;

SELECT ts FROM telemetry LIMIT 20;


SHOW COLUMNS FROM telemetry;


DROP TABLE telemetry;
DROP TABLE energy_yield;
DROP TABLE weather;
DROP TABLE downtime;

SELECT ts FROM telemetry LIMIT 20;

SELECT COUNT(*) FROM v_hourly_telemetry;
SELECT COUNT(*) FROM v_turbine_hourly;


SELECT * FROM telemetry LIMIT 10;

SELECT * FROM energy_yield LIMIT 10;

ALTER TABLE telemetry MODIFY ts DATETIME NOT NULL;
ALTER TABLE energy_yield MODIFY ts DATETIME NOT NULL;
ALTER TABLE weather MODIFY ts DATETIME NOT NULL;
ALTER TABLE downtime MODIFY event_start DATETIME NOT NULL;
ALTER TABLE downtime MODIFY event_end DATETIME NOT NULL;

DROP TABLE energy_yield;
DROP TABLE telemetry;
DROP TABLE weather;
DROP TABLE downtime;




SELECT MIN(ts), MAX(ts), COUNT(*) FROM telemetry;

TRUNCATE TABLE telemetry;
TRUNCATE TABLE energy_yield;
TRUNCATE TABLE weather;
TRUNCATE TABLE downtime;

SELECT MIN(ts), MAX(ts) FROM telemetry;

ALTER TABLE telemetry MODIFY ts DATETIME;
ALTER TABLE energy_yield MODIFY ts DATETIME;
ALTER TABLE weather MODIFY ts DATETIME;
ALTER TABLE downtime MODIFY event_start DATETIME;
ALTER TABLE downtime MODIFY event_end DATETIME;


CREATE OR REPLACE VIEW v_hourly_telemetry AS
SELECT
    turbine_id,
    DATE_FORMAT(ts, '%Y-%m-%d %H:00:00') AS ts_hour,
    AVG(power_kw) AS avg_power_kw,
    AVG(rotor_speed_rpm) AS avg_rotor_speed_rpm,
    AVG(wind_speed_ms) AS wind_ms,
    AVG(wind_direction_deg) AS wind_dir_deg
FROM telemetry
GROUP BY turbine_id, ts_hour;



CREATE OR REPLACE VIEW v_hourly_yield AS
SELECT
    turbine_id,
    DATE_FORMAT(ts, '%Y-%m-%d %H:00:00') AS ts_hour,
    SUM(energy_kwh) AS energy_kwh
FROM energy_yield
GROUP BY turbine_id, ts_hour;



CREATE OR REPLACE VIEW v_hourly_weather AS
SELECT
    DATE_FORMAT(ts, '%Y-%m-%d %H:00:00') AS ts_hour,
    AVG(wind_speed_ms) AS wind_ms,
    AVG(wind_direction_deg) AS wind_dir_deg,
    AVG(temperature_c) AS temp_c,
    AVG(pressure_hpa) AS pressure_hpa,
    AVG(precip_mm) AS precip_mm,
    MAX(icing_flag) AS icing_flag
FROM weather
GROUP BY ts_hour;



CREATE OR REPLACE VIEW v_hourly_downtime AS
SELECT
    t.turbine_id,
    DATE_FORMAT(h.ts, '%Y-%m-%d %H:00:00') AS ts_hour,
    CASE 
        WHEN h.ts BETWEEN d.event_start AND d.event_end THEN 1
        ELSE 0
    END AS is_downtime
FROM telemetry t
JOIN telemetry h ON t.turbine_id = h.turbine_id
LEFT JOIN downtime d
    ON d.turbine_id = t.turbine_id
   AND h.ts BETWEEN d.event_start AND d.event_end;


CREATE OR REPLACE VIEW v_turbine_hourly AS
SELECT
    ht.turbine_id,
    ht.ts_hour,
    ht.avg_power_kw,
    hy.energy_kwh,
    hw.wind_ms,
    hw.temp_c,
    hw.icing_flag,
    hd.is_downtime
FROM v_hourly_telemetry ht
LEFT JOIN v_hourly_yield hy
    ON ht.turbine_id = hy.turbine_id
   AND ht.ts_hour = hy.ts_hour
LEFT JOIN v_hourly_weather hw
    ON ht.ts_hour = hw.ts_hour
LEFT JOIN v_hourly_downtime hd
    ON ht.turbine_id = hd.turbine_id
   AND ht.ts_hour = hd.ts_hour;



