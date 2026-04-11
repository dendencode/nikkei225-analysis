# 本番環境デプロイガイド

## 概要

このドキュメントは、日経225 ETL パイプラインを本番環境にデプロイする手順を記載する。

## アーキテクチャ

┌─────────────────────────────────────────────────┐
│                 本番環境 (AWS)                    │
│                                                   │
│  ┌───────────┐    ┌───────────┐    ┌──────────┐ │
│  │ CloudWatch│    │   Lambda  │    │    S3    │ │
│  │  Events   │───→│  (ETL)   │───→│ (Storage)│ │
│  │ (毎日9時) │    │           │    │          │ │
│  └───────────┘    └───────────┘    └──────────┘ │
│                                         │        │
│                                         ▼        │
│                                   ┌──────────┐   │
│                                   │  Athena  │   │
│                                   │ (分析)   │   │
│                                   └──────────┘   │
└─────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────┐
│              開発環境 (ローカル)                   │
│                                                   │
│  ┌───────────┐    ┌───────────┐    ┌──────────┐ │
│  │  Docker   │    │  Jupyter  │    │  pytest  │ │
│  │  (ETL)    │    │ (分析)    │    │ (テスト) │ │
│  └───────────┘    └───────────┘    └──────────┘ │
│                                                   │
│  GitHub Actions: push → 自動テスト → デプロイ     │
└─────────────────────────────────────────────────┘

## 前提条件

- Docker Desktop がインストールされていること
- AWS CLI がインストール・設定されていること
- Git がインストールされていること

## デプロイ手順

### 1. 環境変数の設定

```bash
cd infrastructure
cp production.env.example .env
# .env を編集して AWS キーなどを設定
```

### 2. Docker での ETL 実行

```bash
# ETL パイプライン実行
docker-compose -f infrastructure/docker-compose.yml run etl

# Jupyter で分析
docker-compose -f infrastructure/docker-compose.yml up jupyter
# → http://localhost:8888 でアクセス
```

### 3. AWS へのデプロイ

```bash
# S3 にデータをアップロード
python src/s3_integration.py

# Lambda 関数のパッケージ作成
zip -r lambda_function.zip src/ requirements.txt

# Lambda にデプロイ
aws lambda create-function \
  --function-name nikkei225-etl \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT:role/YOUR_ROLE \
  --handler src.s3_integration.lambda_handler \
  --zip-file fileb://lambda_function.zip
```

### 4. 定期実行の設定

```bash
# CloudWatch Events で毎日 9:00 に実行
aws events put-rule \
  --name nikkei225-daily-etl \
  --schedule-expression "cron(0 0 ? * MON-FRI *)"

aws events put-targets \
  --rule nikkei225-daily-etl \
  --targets "Id"="1","Arn"="arn:aws:lambda:ap-northeast-1:YOUR_ACCOUNT:function:nikkei225-etl"
```

## 監視・アラート

### CloudWatch ログ

```python
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("ETL Pipeline Started", extra={
    "pipeline": "nikkei225",
    "environment": "production"
})
```

### アラート設定

- Lambda 実行失敗 → SNS でメール通知
- S3 アップロード失敗 → CloudWatch Alarm
- 実行時間が10分超過 → タイムアウトアラート

## ロールバック手順

### データに問題があった場合

```bash
# S3 から前日のバックアップを復元
aws s3 cp s3://nikkei225-data-portfolio/databases/nikkei225_YYYYMMDD.db ./nikkei225.db
```

### コードに問題があった場合

```bash
# 前のバージョンに戻す
git revert HEAD
git push

# Lambda を前のバージョンに戻す
aws lambda update-function-code \
  --function-name nikkei225-etl \
  --zip-file fileb://lambda_function_previous.zip
```

## セキュリティ

### 守るべきルール

1. `.env` ファイルは絶対に Git に上げない
2. AWS アクセスキーはローテーション（定期変更）する
3. S3 バケットはパブリックアクセスを無効にする
4. Lambda の IAM ロールは最小権限の原則に従う
5. CloudWatch ログには機密情報を出力しない

### IAM ポリシー（最小権限）

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:PutObject",
                "s3:GetObject"
            ],
            "Resource": "arn:aws:s3:::nikkei225-data-portfolio/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
            ],
            "Resource": "*"
        }
    ]
}
```