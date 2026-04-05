# 日経225 データ分析ポートフォリオ

##  目的
統計的根拠を持つデータ分析を実装し、記録を残す。

##  実装内容

### 分析ノートブック
- Notebook 1 - データ取得 + 基本統計量 + 可視化
- Notebook 2 - 移動平均戦略 + バックテスト + t検定による有意性検証
- Notebook 3 - 因果推論（Granger因果性テスト + イベント研究）
- Notebook 4 - SQL によるデータ管理（テーブル設計 + 基本クエリ）
- Notebook 5 - SQL 高度活用（Window関数 + ETL連携）

### スクリプト
- src/etl.py - ETL パイプライン（データ取得 → SQL加工 → 統計検定を自動実行）
- src/s3_integration.py - AWS S3 連携（クラウドストレージへのアップロード）

### 主な分析結果
- 移動平均クロスオーバー戦略：平均リターン +2.07%（ただしp=0.68で統計的に有意ではない）
- Granger因果性テスト：金利変化 → 翌日の株価変動に有意な因果関係あり（p=0.024）
- FOMC イベント研究：会合前後で有意な差は認められず（p=0.897）

##  技術スタック
- Python（pandas, numpy, scipy, statsmodels）
- SQL（SQLite, Window関数, サブクエリ）
- Docker（コンテナ化）
- AWS（S3, Lambda 設計済み）
- Git / GitHub

##  進捗
- [x] テクニカル分析 + t検定
- [x] 因果推論（Granger テスト）
- [x] SQL データ管理 + Window関数
- [x] ETL スクリプト化
- [x] Docker 環境構築
- [x] AWS S3 連携（コード実装済み）
- [ ] README 最終版 + 応募準備（Day 7）
- [ ] SQL 最適化（Day 8）
- [ ] dbt データ変換（Day 9）
- [ ] Airflow 自動化（Day 10）

##  実行方法
```bash
pip install -r requirements.txt
jupyter notebook

# ETL パイプライン実行
python src/etl.py

# Docker で実行
docker build -t nikkei225 .
docker run nikkei225
```