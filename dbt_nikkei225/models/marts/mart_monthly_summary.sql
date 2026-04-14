-- Marts: 月次サマリー（Data Mart）
SELECT
    SUBSTR(date, 1, 4) AS year,
    SUBSTR(date, 6, 2) AS month,
    SUBSTR(date, 1, 4) || '-' || SUBSTR(date, 6, 2) AS year_month,
    COUNT(*) AS trading_days,
    ROUND(AVG(close_price), 2) AS avg_close,
    ROUND(MAX(close_price), 2) AS max_close,
    ROUND(MIN(close_price), 2) AS min_close,
    ROUND(AVG(daily_return), 4) AS avg_daily_return,
    SUM(CASE WHEN daily_return > 0 THEN 1 ELSE 0 END) AS up_days,
    SUM(CASE WHEN daily_return < 0 THEN 1 ELSE 0 END) AS down_days
FROM {{ ref('int_daily_metrics') }}
WHERE daily_return IS NOT NULL
GROUP BY SUBSTR(date, 1, 4), SUBSTR(date, 6, 2)
ORDER BY year, month