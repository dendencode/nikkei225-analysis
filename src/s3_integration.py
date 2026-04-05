"""
AWS S3　連係スクリプト

使用方法:
    1. AWS CLIをインストール: pip install boto3 awscli
    2. AWS 認証設定: aws configure
    3. 実行: python src/s3_integration.py
"""

import os
import sys
import sqlite3
import pandas as pd
from datetime import datetime


#設定
BUCKET_NAME = 'nikkei225-data-portfolio'
DB_PATH = 'nikkei225.db'
S3_KEY_PREFIX = 'databases'

def check_aws_credentials():
    """AWS 認証情報が設定されているか確認"""
    try:
        import boto3
        sts = boto3.client('sts')
        identity = sts.get_caller_identity()
        print(f" ✓ AWS 認証OK (アカウント: )")
        return True
    except ImportError:
        print(" × boto3　がインストールされていません")
        print("  → pip install boto3 awscli")
        return False
    except Exception as e:
        print(f"  ✗ AWS 認証エラー: {e}")
        print("    → aws configure で認証情報を設定してください")
        return False
    

def upload_to_s3(dry_run=False):
    """ローカルの SQLite を S3 にアップロード"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    s3_key = f"{S3_KEY_PREFIX}/nikkei225_{timestamp}.db"

    print(f"\n[UPLOAD] データを S3 にアップロード")
    print(f"  ファイル: {DB_PATH}")
    print(f"  宛先:     s3://{BUCKET_NAME}/{s3_key}")

    if dry_run:
        print(f"  ⚠ DRY RUN モード（実際にはアップロードしません）")
        # ファイルの存在確認だけ行う
        if os.path.exists(DB_PATH):
            size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)
            print(f"  ✓ ファイル確認OK（{size_mb:.2f} MB）")
        else:
            print(f"  ✗ ファイルが見つかりません: {DB_PATH}")
        return

    import boto3
    s3 = boto3.client('s3', region_name='ap-northeast-1')
    s3.upload_file(
        Filename=DB_PATH,
        Bucket=BUCKET_NAME,
        Key=s3_key
    )
    print(f"  ✓ アップロード完了")


def download_from_s3(dry_run=False):
    """S3 からダウンロードして内容を確認"""
    print(f"\n[DOWNLOAD] S3 からデータをダウンロード")

    if dry_run:
        print(f"  ⚠ DRY RUN モード（ローカルDBで代替確認）")
        # ローカルのDBで動作確認
        if os.path.exists(DB_PATH):
            conn = sqlite3.connect(DB_PATH)
            result = pd.read_sql(
                "SELECT COUNT(*) as total FROM raw_nikkei225", conn
            )
            print(f"  ✓ ローカルDB確認: {result['total'][0]} 行のデータ")
            conn.close()
        return

    import boto3
    s3 = boto3.client('s3', region_name='ap-northeast-1')
    s3.download_file(
        Bucket=BUCKET_NAME,
        Key=f"{S3_KEY_PREFIX}/nikkei225_latest.db",
        Filename='nikkei225_from_s3.db'
    )
    conn = sqlite3.connect('nikkei225_from_s3.db')
    result = pd.read_sql(
        "SELECT COUNT(*) as total FROM raw_nikkei225", conn
    )
    print(f"  ✓ ダウンロード確認: {result['total'][0]} 行のデータ")
    conn.close()

def show_architecture():
    """アーキテクチャの説明を表示"""
    print("""
╔══════════════════════════════════════════════════════╗
║           AWS S3 連携アーキテクチャ                  ║
╠══════════════════════════════════════════════════════╣
║                                                      ║
║  [Local / Docker]                                    ║
║       │                                              ║
║       │  python src/etl.py                           ║
║       ▼                                              ║
║  ┌──────────┐    ┌──────────┐    ┌──────────┐       ║
║  │ Extract  │ →  │Transform │ →  │   Load   │       ║
║  │ yfinance │    │  SQLite  │    │  分析    │       ║
║  └──────────┘    └──────────┘    └──────────┘       ║
║                       │                              ║
║                       │  python src/s3_integration.py ║
║                       ▼                              ║
║              ┌──────────────┐                        ║
║              │   AWS S3     │                        ║
║              │  (クラウド)  │                        ║
║              └──────────────┘                        ║
║                       │                              ║
║                       ▼                              ║
║              ┌──────────────┐                        ║
║              │ AWS Lambda   │                        ║
║              │ (定期実行)   │                        ║
║              └──────────────┘                        ║
║                                                      ║
╚══════════════════════════════════════════════════════╝
""")

def lambda_handler(event, context):
    """
    AWS Lambda ハンドラ(定期実行用)
    
    CloudWatch Eventsで毎日9:00に実行する想定。
    Lambdaにデプロイする場合、この関数がエントリーポイントになる。
    """
    from etl import extract, transform, load

    print("Lambda関数が起動しました")

    df = extract()
    transform(df)
    load()
    upload_to_s3()

    return{
        'statusCode': 200,
        'body': 'ETL　パイプライン完了'
    }

def main():
    """S# 連係のメイン処理"""
    dry_run = '--dry-run' in sys.argv

    print("=" * 60)
    print("AWS S3 連携")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if dry_run:
        print("モード: DRY RUN（AWS への実際の通信なし）")
    print("=" * 60)

    # アーキテクチャ表示
    show_architecture()

    if not dry_run:
        # AWS 認証確認
        print("[AUTH] AWS 認証確認...")
        if not check_aws_credentials():
            print("\n→ --dry-run オプションで動作確認できます：")
            print("  python src/s3_integration.py --dry-run")
            return

    # アップロード
    upload_to_s3(dry_run=dry_run)

    # ダウンロード確認
    download_from_s3(dry_run=dry_run)

    print("\n" + "=" * 60)
    print("✓ S3 連携処理完了")
    print("=" * 60)


if __name__ == '__main__':
    main()