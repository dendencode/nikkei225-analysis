"""
ETL スクリプト: yfinance→ SQLite → 分析

使用方法:
    python src/etl.py

このスクリプトは以下を実行:
1. Extract: yfinanceから日経225データを取得
2. Transform: SQLiteに保存し、Window関数で移動平均を計算
3. Load:　　結果を確認・表示
"""

import sqlite3
import pandas as pd
import numpy as np
import yfinance as yf
from scipy import stats
from datetime import datetime


def extract():
    """yfinanceからデータ取得"""
    print("[EXTRACT] yfinance からデータ取得中．．．")
    nikkei = yf.download('^N225', start = '2019-01-01')
    nikkei.columns = nikkei.columns.get_level_values(0)
    print(f" ✓{len(nikkei)}行のデータを取得")
    return nikkei

def transform(df, db_path='nikkei225.db'):
    """SQLiteでデータ変換"""
    print("[TRANSFORM]SQLiteでデータ変換中...")

    conn = sqlite3.connect(db_path)

    #Rawテーブルに保存
    df_for_sql =  df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    df_for_sql.index = df_for_sql.index.strftime('%Y-%m-%d')
    df_for_sql.index.name = 'date'
    df_for_sql.to_sql('raw_nikkei225', conn, if_exists='replace')
    print(f"  ✓ raw_nikkei225 テーブルに {len(df)} 行を INSERT")

    # Window関数で移動平均を計算
    conn.execute("DROP TABLE IF EXISTS with_moving_avg")
    conn.execute("""
        CREATE TABLE with_moving_avg AS
        SELECT 
            date,
            Close as close,
            ROUND(AVG(Close) OVER (
                ORDER BY date 
                ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
            ), 2) as ma_20,
            ROUND(AVG(Close) OVER (
                ORDER BY date 
                ROWS BETWEEN 199 PRECEDING AND CURRENT ROW
            ), 2) as ma_200
        FROM raw_nikkei225
        ORDER BY date
    """)
    conn.commit()
    print("  ✓ with_moving_avg テーブル作成（Window関数で移動平均計算）")

    # 月次集計テーブル
    conn.execute("DROP TABLE IF EXISTS processed_monthly")
    conn.execute("""
        CREATE TABLE processed_monthly AS
        SELECT 
            SUBSTR(date, 1, 7) as month,
            ROUND(AVG(Close), 2) as avg_close,
            ROUND(MAX(Close), 2) as max_close,
            ROUND(MIN(Close), 2) as min_close,
            COUNT(*) as trading_days,
            ROUND((MAX(Close) - MIN(Close)) / MIN(Close) * 100, 2) as price_range_pct
        FROM raw_nikkei225
        GROUP BY SUBSTR(date, 1, 7)
        ORDER BY month
    """)
    conn.commit()
    print("  ✓ processed_monthly テーブル作成（月次集計）")

    conn.close()


def load(db_path='nikkei225.db'):
    """結果を確認・統計検定"""
    print("[LOAD] 結果確認 + 統計検定...")

    conn = sqlite3.connect(db_path)

    # データ統計
    stats_df = pd.read_sql("""
        SELECT 
            COUNT(*) as total_rows, 
            MIN(date) as start_date, 
            MAX(date) as end_date 
        FROM raw_nikkei225
    """, conn)
    print(f"  データ期間: {stats_df['start_date'][0]} 〜 {stats_df['end_date'][0]}")
    print(f"  総行数: {stats_df['total_rows'][0]}")

    # 移動平均の最新値
    latest = pd.read_sql("""
        SELECT date, close, ma_20, ma_200 
        FROM with_moving_avg 
        ORDER BY date DESC LIMIT 5
    """, conn)
    print(f"\n  【最新5日の移動平均】")
    print(f"  {latest.to_string(index=False)}")

    # クロスオーバーシグナルでトレード分析
    signals = pd.read_sql("""
        SELECT date, close, ma_20, ma_200,
            CASE 
                WHEN ma_20 > ma_200 
                     AND LAG(ma_20) OVER (ORDER BY date) <= LAG(ma_200) OVER (ORDER BY date)
                THEN 'BUY'
                WHEN ma_20 < ma_200 
                     AND LAG(ma_20) OVER (ORDER BY date) >= LAG(ma_200) OVER (ORDER BY date)
                THEN 'SELL'
                ELSE NULL
            END as signal
        FROM with_moving_avg
        WHERE ma_200 IS NOT NULL
    """, conn)

    signals_only = signals[signals['signal'].notna()]
    buy_rows = signals_only[signals_only['signal'] == 'BUY'].reset_index(drop=True)
    sell_rows = signals_only[signals_only['signal'] == 'SELL'].reset_index(drop=True)

    trades = []
    for i, buy in buy_rows.iterrows():
        future_sells = sell_rows[sell_rows['date'] > buy['date']]
        if len(future_sells) > 0:
            sell = future_sells.iloc[0]
            return_pct = (sell['close'] - buy['close']) / buy['close'] * 100
            trades.append({'return_pct': return_pct})

    if trades:
        returns = [t['return_pct'] for t in trades]
        t_stat, p_value = stats.ttest_1samp(returns, 0)

        print(f"\n  【t検定結果】")
        print(f"  トレード数:   {len(returns)}")
        print(f"  平均リターン: {np.mean(returns):.4f}%")
        print(f"  p値:          {p_value:.6f}")
        if p_value < 0.05:
            print(f"  → 統計的に有意（p < 0.05）")
        else:
            print(f"  → 統計的に有意ではない（p >= 0.05）")

    conn.close()


def main():
    """ETL パイプライン実行"""
    print("=" * 60)
    print("日経225 ETL パイプライン")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    try:
        df = extract()
        transform(df)
        load()

        print("\n" + "=" * 60)
        print("✓ ETL パイプライン完了")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ エラー: {e}")
        raise


if __name__ == '__main__':
    main()