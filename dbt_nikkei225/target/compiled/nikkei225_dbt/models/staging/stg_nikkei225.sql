-- Staging: 生データの整理（列名統一、型変換、NULL除外）
SELECT
    date,
    ROUND(CAST("Open" AS REAL), 2) AS open_price,
    ROUND(CAST("High" AS REAL), 2) AS high_price,
    ROUND(CAST("Low" AS REAL), 2) AS low_price,
    ROUND(CAST("Close" AS REAL), 2) AS close_price,
    CAST("Volume" AS INTEGER) AS volume
FROM main."raw_nikkei225"
WHERE "Close" IS NOT NULL
ORDER BY date