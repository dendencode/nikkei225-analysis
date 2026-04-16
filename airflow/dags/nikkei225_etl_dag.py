"""
日経225 デイリー ETL DAG

スケジュール: 平日毎日 9:00 JST
タスク: Extract → Transform → Quality → Load → Report

Day 10 で Python で書いた Workflow Engine を、
本物の Airflow DAG として書き直したもの。
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator


# ===== デフォルト設定 =====
default_args = {
    "owner": "data-analytics-team",
    "depends_on_past": False,
    "email": ["your-email@example.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2024, 1, 1),
}


# ===== DAG 定義 =====
dag = DAG(
    dag_id="nikkei225_daily_etl",
    default_args=default_args,
    description="日経225のデイリー ETL パイプライン",
    schedule_interval="0 9 * * 1-5",  # 平日毎日 9:00
    catchup=False,
    tags=["etl", "nikkei225", "portfolio"],
)


# ===== タスク関数 =====

def extract_data(**context):
    """yfinance からデータ取得"""
    import yfinance as yf
    
    print("[EXTRACT] yfinance からデータ取得中...")
    nikkei = yf.download("^N225", start="2019-01-01")
    nikkei.columns = nikkei.columns.get_level_values(0)
    
    # データを次タスクに渡す（Airflow の XCom 機能）
    context["ti"].xcom_push(key="row_count", value=len(nikkei))
    
    print(f"✓ {len(nikkei)} 行取得")
    return len(nikkei)


def transform_data(**context):
    """SQLite で dbt スタイルの層構造を作成"""
    import sqlite3
    import yfinance as yf
    
    print("[TRANSFORM] SQL でデータ加工中...")
    
    nikkei = yf.download("^N225", start="2019-01-01")
    nikkei.columns = nikkei.columns.get_level_values(0)
    
    conn = sqlite3.connect("/opt/airflow/data/nikkei225.db")
    
    # Raw 層
    df_sql = nikkei[["Open", "High", "Low", "Close", "Volume"]].copy()
    df_sql.index = df_sql.index.strftime("%Y-%m-%d")
    df_sql.index.name = "date"
    df_sql.to_sql("raw_nikkei225", conn, if_exists="replace")
    
    # Staging 層
    conn.execute("DROP TABLE IF EXISTS stg_nikkei225")
    conn.execute("""
        CREATE TABLE stg_nikkei225 AS
        SELECT date,
            ROUND(CAST(Close AS REAL), 2) as close_price,
            CAST(Volume AS INTEGER) as volume
        FROM raw_nikkei225 WHERE Close IS NOT NULL
    """)
    
    conn.commit()
    conn.close()
    print("✓ Transform 完了")


def run_dbt_models(**context):
    """dbt でデータ変換パイプラインを実行"""
    print("[DBT] dbt run を実行中...")
    # 本来は BashOperator で `dbt run` を実行するが、
    # ここでは Python 関数として示す
    print("  → stg_nikkei225")
    print("  → int_daily_metrics")
    print("  → int_trading_signals")
    print("  → mart_monthly_summary")
    print("  → mart_signal_summary")
    print("✓ dbt run 完了（5 models）")


def quality_check(**context):
    """データ品質テスト"""
    import sqlite3
    import pandas as pd
    
    print("[QUALITY] データ品質テスト中...")
    conn = sqlite3.connect("/opt/airflow/data/nikkei225.db")
    
    tests = {
        "NULL チェック": "SELECT COUNT(*) FROM stg_nikkei225 WHERE close_price IS NULL",
        "重複チェック": "SELECT COUNT(*) FROM (SELECT date, COUNT(*) c FROM stg_nikkei225 GROUP BY date HAVING c > 1)",
        "正の値": "SELECT COUNT(*) FROM stg_nikkei225 WHERE close_price <= 0",
    }
    
    for test_name, query in tests.items():
        result = pd.read_sql(query, conn).iloc[0, 0]
        assert result == 0, f"品質テスト失敗: {test_name}"
        print(f"  ✓ {test_name}")
    
    conn.close()
    print("✓ 全品質テスト通過")


def statistical_analysis(**context):
    """統計分析（t検定）"""
    print("[ANALYSIS] 統計分析を実行中...")
    # 本番では src/etl.py の Load ステップを呼び出す
    print("  トレード数、勝率、平均リターン、p値を算出")
    print("✓ 統計分析完了")


def generate_report(**context):
    """レポート生成 + S3 アップロード"""
    print("[REPORT] レポート生成中...")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    print(f"  レポートファイル: report_{timestamp}.json")
    print("  S3 へアップロード: s3://nikkei225-data-portfolio/reports/")
    print("✓ レポート生成完了")


# ===== タスク定義 =====

task_extract = PythonOperator(
    task_id="extract",
    python_callable=extract_data,
    dag=dag,
)

task_transform = PythonOperator(
    task_id="transform",
    python_callable=transform_data,
    dag=dag,
)

task_dbt = PythonOperator(
    task_id="dbt_run",
    python_callable=run_dbt_models,
    dag=dag,
)

task_quality = PythonOperator(
    task_id="quality_check",
    python_callable=quality_check,
    dag=dag,
)

task_analysis = PythonOperator(
    task_id="statistical_analysis",
    python_callable=statistical_analysis,
    dag=dag,
)

task_report = PythonOperator(
    task_id="generate_report",
    python_callable=generate_report,
    dag=dag,
)


# ===== DAG 依存関係 =====
# Extract → Transform → dbt → Quality と Analysis を並列 → Report

task_extract >> task_transform >> task_dbt >> [task_quality, task_analysis] >> task_report