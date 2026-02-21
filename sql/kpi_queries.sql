-- 1. Overall punctuality and breach rates
SELECT
    COUNT(*) AS total_trips,
    SUM(CASE WHEN delay_mins <= sla_threshold_mins THEN 1 ELSE 0 END) AS on_time_trips,
    SUM(breached) AS breached_trips,
    ROUND(100.0 * SUM(CASE WHEN delay_mins <= sla_threshold_mins THEN 1 ELSE 0 END) / COUNT(*), 2) AS punctuality_pct,
    ROUND(100.0 * SUM(breached) / COUNT(*), 2) AS breach_pct,
    ROUND(AVG(delay_mins), 2) AS avg_delay_mins
FROM trips;


-- 2. Zone-wise monthly punctuality trend
SELECT
    t.zone,
    strftime('%Y-%m', tr.trip_date) AS month,
    COUNT(*) AS total_trips,
    SUM(CASE WHEN tr.delay_mins <= tr.sla_threshold_mins THEN 1 ELSE 0 END) AS on_time_trips,
    ROUND(100.0 * SUM(CASE WHEN tr.delay_mins <= tr.sla_threshold_mins THEN 1 ELSE 0 END) / COUNT(*), 2) AS punctuality_pct,
    ROUND(AVG(tr.delay_mins), 2) AS avg_delay_mins
FROM trips tr
JOIN trains t ON tr.train_id = t.train_id
GROUP BY t.zone, strftime('%Y-%m', tr.trip_date)
ORDER BY t.zone, month;


-- 3. Zone ranking by punctuality
SELECT
    t.zone,
    COUNT(*) AS total_trips,
    ROUND(100.0 * SUM(CASE WHEN tr.delay_mins <= tr.sla_threshold_mins THEN 1 ELSE 0 END) / COUNT(*), 2) AS punctuality_pct,
    ROUND(AVG(tr.delay_mins), 2) AS avg_delay_mins
FROM trips tr
JOIN trains t ON tr.train_id = t.train_id
GROUP BY t.zone
ORDER BY punctuality_pct DESC;


-- 4. Top 10 worst-performing trains
SELECT
    t.train_id,
    t.train_name,
    t.train_type,
    t.zone,
    COUNT(*) AS total_trips,
    ROUND(100.0 * SUM(tr.breached) / COUNT(*), 2) AS breach_pct,
    ROUND(AVG(tr.delay_mins), 2) AS avg_delay_mins
FROM trips tr
JOIN trains t ON tr.train_id = t.train_id
GROUP BY t.train_id, t.train_name, t.train_type, t.zone
ORDER BY breach_pct DESC
LIMIT 10;


-- 5. Breach rate by train type
SELECT
    t.train_type,
    COUNT(*) AS total_trips,
    SUM(tr.breached) AS breached_trips,
    ROUND(100.0 * SUM(tr.breached) / COUNT(*), 2) AS breach_pct,
    ROUND(AVG(tr.delay_mins), 2) AS avg_delay_mins
FROM trips tr
JOIN trains t ON tr.train_id = t.train_id
GROUP BY t.train_type
ORDER BY breach_pct DESC;


-- 6. Complaints SLA by zone and category
SELECT
    zone,
    category,
    COUNT(*) AS total_complaints,
    SUM(met_sla) AS met_sla_count,
    ROUND(100.0 * SUM(met_sla) / COUNT(*), 2) AS sla_met_pct,
    ROUND(AVG(resolved_in_days), 2) AS avg_resolution_days
FROM complaints
GROUP BY zone, category
ORDER BY zone, sla_met_pct;


-- 7. Monthly complaint SLA trend
SELECT
    strftime('%Y-%m', filed_date) AS month,
    COUNT(*) AS total_complaints,
    ROUND(100.0 * SUM(met_sla) / COUNT(*), 2) AS sla_met_pct,
    ROUND(AVG(resolved_in_days), 2) AS avg_resolution_days
FROM complaints
GROUP BY strftime('%Y-%m', filed_date)
ORDER BY month;
