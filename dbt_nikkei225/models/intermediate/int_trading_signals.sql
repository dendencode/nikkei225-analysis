-- Intermediate: トレーディングシグナル（クロスオーバー検出）
SELECT
    date,
    close_price,
    ma_20,
    ma_200,
    daily_return,
    CASE
        WHEN ma_20 > ma_200
             AND LAG(ma_20) OVER (ORDER BY date) <= LAG(ma_200) OVER (ORDER BY date)
        THEN 'BUY'
        WHEN ma_20 < ma_200
             AND LAG(ma_20) OVER (ORDER BY date) >= LAG(ma_200) OVER (ORDER BY date)
        THEN 'SELL'
        ELSE NULL
    END AS signal,
    CASE
        WHEN ma_20 > ma_200 THEN 'BULLISH'
        ELSE 'BEARISH'
    END AS trend
FROM {{ ref('int_daily_metrics') }}
WHERE ma_200 IS NOT NULL
ORDER BY date