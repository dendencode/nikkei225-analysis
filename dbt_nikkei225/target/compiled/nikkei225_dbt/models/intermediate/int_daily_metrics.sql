-- Intermediate: 日次メトリクス（リターン + 移動平均）
SELECT
    date,
    close_price,
    volume,
    ROUND(
        (close_price - LAG(close_price) OVER (ORDER BY date))
        / LAG(close_price) OVER (ORDER BY date) * 100,
        4
    ) AS daily_return,
    ROUND(AVG(close_price) OVER (
        ORDER BY date ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ), 2) AS ma_20,
    ROUND(AVG(close_price) OVER (
        ORDER BY date ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
    ), 2) AS ma_200
FROM main."stg_nikkei225"
ORDER BY date