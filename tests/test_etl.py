"""
ETL パイプラインのテスト

実行方法:
    pytest tests/ ~v
"""

import pytest
import sqlite3
import pandas as pd
import os
import sys

# srcフォルダをインポートパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# テスト用のデータベースを準備

@pytest.fixture
def test_db(tmp_path):
    """テスト用の一時データベースを作成"""
    db_path = str(tmp_path / "test_nikkei225.db")
    conn = sqlite3.connect(db_path)
    
    # テスト用データを作成
    conn.execute("""
        CREATE TABLE raw_nikkei225 (
            date TEXT PRIMARY KEY,
            Open REAL,
            High REAL,
            Low REAL,
            Close REAL,
            Volume INTEGER
        )
    """)
    
    test_data = [
        ('2024-01-01', 30000, 30500, 29800, 30200, 1000000),
        ('2024-01-02', 30200, 30800, 30100, 30500, 1100000),
        ('2024-01-03', 30500, 30600, 30000, 30100, 900000),
        ('2024-01-04', 30100, 31000, 30000, 30800, 1200000),
        ('2024-01-05', 30800, 31200, 30500, 31000, 1050000),
    ]
    
    conn.executemany(
        "INSERT INTO raw_nikkei225 VALUES (?, ?, ?, ?, ?, ?)",
        test_data
    )
    conn.commit()
    conn.close()
    
    return db_path

# 1. データベーステスト
class TestDatabase:
    """データベースの基本機能テスト"""
    
    def test_table_exists(self, test_db):
        """テーブルが正しく作成されているか"""
        conn = sqlite3.connect(test_db)
        tables = pd.read_sql(
            "SELECT name FROM sqlite_master WHERE type='table'",
            conn
        )
        conn.close()
        assert 'raw_nikkei225' in tables['name'].values
    
    def test_row_count(self, test_db):
        """データの行数が正しいか"""
        conn = sqlite3.connect(test_db)
        count = pd.read_sql("SELECT COUNT(*) as cnt FROM raw_nikkei225", conn)
        conn.close()
        assert count['cnt'][0] == 5
    
    def test_no_null_close(self, test_db):
        """終値に NULL がないか"""
        conn = sqlite3.connect(test_db)
        nulls = pd.read_sql(
            "SELECT COUNT(*) as cnt FROM raw_nikkei225 WHERE Close IS NULL",
            conn
        )
        conn.close()
        assert nulls['cnt'][0] == 0
    def test_no_duplicate_dates(self, test_db):
        """日付に重複がないか"""
        conn = sqlite3.connect(test_db)
        dupes = pd.read_sql(
            "SELECT COUNT(*) as cnt FROM (SELECT date, COUNT(*) c FROM raw_nikkei225 GROUP BY date HAVING c > 1)",
            conn
        )
        conn.close()
        assert dupes['cnt'][0] == 0
    
    def test_positive_prices(self, test_db):
        """株価が正の値か"""
        conn = sqlite3.connect(test_db)
        negatives = pd.read_sql(
            "SELECT COUNT(*) as cnt FROM raw_nikkei225 WHERE Close <= 0",
            conn
        )
        conn.close()
        assert negatives['cnt'][0] == 0

# 2. SQL 変換テスト

class TestTransform:
    """SQL 変換処理のテスト"""
    
    def test_staging_creation(self, test_db):
        """staging テーブルが正しく作成されるか"""
        conn = sqlite3.connect(test_db)
        
        conn.execute("""
            CREATE TABLE stg_nikkei225 AS
            SELECT 
                date,
                ROUND(CAST(Close AS REAL), 2) as close_price,
                CAST(Volume AS INTEGER) as volume
            FROM raw_nikkei225
            WHERE Close IS NOT NULL
            ORDER BY date
        """)
        conn.commit()
        
        count = pd.read_sql("SELECT COUNT(*) as cnt FROM stg_nikkei225", conn)
        conn.close()
        assert count['cnt'][0] == 5
    
    def test_moving_average_calculation(self, test_db):
        """移動平均の計算が正しいか"""
        conn = sqlite3.connect(test_db)
        
        result = pd.read_sql("""
            SELECT 
                date,
                Close,
                ROUND(AVG(Close) OVER (
                    ORDER BY date ROWS BETWEEN 1 PRECEDING AND CURRENT ROW
                ), 2) as ma_2
            FROM raw_nikkei225
            ORDER BY date
        """, conn)
        conn.close()
        
        # 2行目：(30200 + 30500) / 2 = 30350
        assert abs(result.iloc[1]['ma_2'] - 30350.0) < 1.0
    
    def test_daily_return_calculation(self, test_db):
        """日次リターンの計算が正しいか"""
        conn = sqlite3.connect(test_db)
        
        result = pd.read_sql("""
            SELECT 
                date,
                Close,
                ROUND(
                    (Close - LAG(Close) OVER (ORDER BY date))
                    / LAG(Close) OVER (ORDER BY date) * 100,
                    4
                ) as daily_return
            FROM raw_nikkei225
            ORDER BY date
        """, conn)
        conn.close()
        
        # 2行目：(30500 - 30200) / 30200 * 100 = 0.9934%
        expected = (30500 - 30200) / 30200 * 100
        assert abs(result.iloc[1]['daily_return'] - expected) < 0.01

# 3. データ品質テスト
class TestDataQuality:
    """データ品質の検証テスト"""
    
    def test_date_format(self, test_db):
        """日付が YYYY-MM-DD 形式か"""
        conn = sqlite3.connect(test_db)
        bad_dates = pd.read_sql(
            "SELECT COUNT(*) as cnt FROM raw_nikkei225 WHERE date NOT LIKE '____-__-__'",
            conn
        )
        conn.close()
        assert bad_dates['cnt'][0] == 0
    
    def test_high_greater_than_low(self, test_db):
        """高値が安値以上か"""
        conn = sqlite3.connect(test_db)
        violations = pd.read_sql(
            "SELECT COUNT(*) as cnt FROM raw_nikkei225 WHERE High < Low",
            conn
        )
        conn.close()
        assert violations['cnt'][0] == 0
    
    def test_close_within_range(self, test_db):
        """終値が高値と安値の範囲内か"""
        conn = sqlite3.connect(test_db)
        violations = pd.read_sql(
            "SELECT COUNT(*) as cnt FROM raw_nikkei225 WHERE Close > High OR Close < Low",
            conn
        )
        conn.close()
        assert violations['cnt'][0] == 0
    
    def test_volume_non_negative(self, test_db):
        """出来高が負でないか"""
        conn = sqlite3.connect(test_db)
        violations = pd.read_sql(
            "SELECT COUNT(*) as cnt FROM raw_nikkei225 WHERE Volume < 0",
            conn
        )
        conn.close()
        assert violations['cnt'][0] == 0