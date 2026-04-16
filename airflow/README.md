# Airflow セットアップ

## 概要

Apache Airflow を使ったワークフロー自動化の実装。
Day 10 で Python で作った Workflow Engine を、本物の Airflow DAG に置き換えたもの。

## 起動方法

```bash
# Airflow を起動（初回は5〜10分かかる）
cd airflow
docker-compose -f docker-compose.airflow.yml up airflow-init
docker-compose -f docker-compose.airflow.yml up -d

# Web UI にアクセス
# http://localhost:8080
# ユーザー名: admin
# パスワード: admin
```

## DAG の構造
Extract（yfinance）
↓
Transform（SQLite）
↓
dbt run（dbt モデル実行）
↓
┌─────┴─────┐
↓           ↓
Quality    Analysis
（品質テスト）（統計分析）
↓           ↓
└─────┬─────┘
↓
Report（レポート生成）

## スケジュール
schedule_interval = "0 9 * * 1-5" → 平日毎日 9:00 JST に自動実行

## 停止方法

```bash
docker-compose -f docker-compose.airflow.yml down
```

## 今後の拡張

- Slack 通知の追加
- dbt Cloud 連携
- S3 へのレポート自動アップロード
- CloudWatch メトリクスとの統合

