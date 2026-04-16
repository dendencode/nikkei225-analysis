-- Marts: シグナル別の集計
SELECT
    signal,
    COUNT(*) AS signal_count,
    ROUND(AVG(close_price), 2) AS avg_price_at_signal,
    ROUND(MIN(close_price), 2) AS min_price,
    ROUND(MAX(close_price), 2) AS max_price
FROM {{ ref('int_trading_signals') }}
WHERE signal IS NOT NULL
GROUP BY signal