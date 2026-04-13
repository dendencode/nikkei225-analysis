# 日経225 データ分析ポートフォリオ

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## プロジェクト概要

日経225の過去7年分、1700日以上のデータを使い、統計的根拠に基づくデータ分析と本番環境を想定したETLパイプラインを実装したポートフォリオです。

「なんとなく分析」ではなく、統計検定（t検定）で戦略の有意性を検証し、Granger因果性テストで因果関係を証明するなど、科学的な根拠に基づく分析を重視しています。

分析結果が統計的に有意でなかった場合も正直に報告し、その原因（サンプルサイズ不足、標準偏差の大きさ）を特定しています。
---

##  このプロジェクトで示すスキル

### 分析スキル

| 手法 | 実装内容 | ビジネス価値 |
|---|---|---|
| 時系列分析 | 移動平均クロスオーバー戦略 | トレンド検出の自動化 |
| 統計検定 | t検定で有意性を検証（p値による判定） | 「運ではなく実力」を証明 |
| 因果推論 | Grangerテストで金利→株価の因果関係を測定 | 外部要因の定量的評価 |

### データエンジニアリングスキル

| スキル | 実装内容 | 実務への応用 |
|---|---|---|
| SQL | Window関数、JOIN、サブクエリ、CASE文、インデックス | データウェアハウスでの加工 |
| テーブル設計 | 正規化（Dimension/Factテーブル）、Star Schema | 大規模DB設計 |
| ETLパイプライン | Python スクリプトで Extract→Transform→Load を自動化 | 本番環境での定期実行 |
| データ品質 | NULL/重複/範囲/フォーマットの自動テスト（6項目） | データ信頼性の担保 |
| Docker | コンテナ化 + docker-compose で環境を完全再現 | チーム開発での環境統一 |
| AWS設計 | S3連携 + Lambda定期実行のアーキテクチャ | サーバーレス分析基盤 |
| CI/CD | pytest（12テスト）+ GitHub Actions で自動テスト | コード品質の自動保証 |
| ワークフロー | DAG依存関係 + リトライ + ログ記録（Airflowスタイル） | 運用のレジリエンス |
| データ変換 | raw→staging→intermediate→marts の層構造（dbtスタイル） | Data Mart 設計 |

---

##  プロジェクト構成

```
nikkei225-analysis/
├── notebooks/
│   ├── 1_data_acquisition.ipynb        # データ取得 + 基本統計
│   ├── 2_technical_analysis.ipynb      # 移動平均 + バックテスト + t検定
│   ├── 3_causal_inference.ipynb        # 因果推論（Granger + イベント研究）
│   ├── 4_data_preparation_sql.ipynb    # SQL基礎（テーブル設計 + クエリ）
│   ├── 5_sql_advanced.ipynb            # SQL応用（Window関数 + ETL連携）
│   ├── 6_sql_optimization.ipynb        # SQL最適化（正規化 + JOIN + インデックス）
│   ├── 7_dbt_style_pipeline.ipynb      # dbtスタイル層構造 + データ品質テスト
│   ├── 8_workflow_automation.ipynb     # Airflowスタイル DAG + ワークフロー
│   └── 10_final_test.ipynb             # 最終テスト + パフォーマンス計測
│
├── src/
│   ├── etl.py                          # ETLパイプライン
│   └── s3_integration.py              # AWS S3 連携
│
├── tests/
│   └── test_etl.py                     # pytest テスト（12件）
│
├── infrastructure/
│   ├── docker-compose.yml              # マルチコンテナ構成
│   ├── production.env.example          # 本番環境変数テンプレート
│   └── DEPLOYMENT.md                   # デプロイガイド
│
├── .github/workflows/
│   └── test.yml                        # GitHub Actions CI/CD
│
├── Dockerfile                          # コンテナ化
├── requirements.txt                    # Python依存パッケージ
├── .gitignore
└── README.md
```

---

##  分析結果のハイライト

### 1. テクニカル分析：MA20 × MA200 クロスオーバー戦略

移動平均のゴールデンクロス（買い）とデッドクロス（売り）で売買した結果を統計検定で評価。

```
完了トレード数: 12件
勝率:          16.7%（勝ち2件 / 負け10件）
平均リターン:  +1.34%

【t検定結果】
t統計量 = 0.33
p値     = 0.745

【結論】
統計的に有意ではない（p ≥ 0.05）。
平均リターンはプラスだが、標準偏差（14%）が大きく、
「たまたまプラスになった」可能性を排除できない。
勝率は低いが、少数の大勝ち（+24.7%, +35.5%）が損失をカバーする構造。
```

### 2. 因果推論：米国金利 → 日経225 への影響

米国10年国債利回りの変化が日経225の株価変動を引き起こしているかを検証。

```
【相関分析】
相関係数 = 0.077（非常に弱い → 同じ日の連動はほぼない）

【Granger因果性テスト】
ラグ1（翌日）: 因果あり（p < 0.05）
ラグ2（2日後）: 因果あり（p < 0.05）
ラグ3〜5:      有意ではない

【結論】
金利変化は翌日〜2日後の株価変動を予測する力がある。
同じ日には反応しないが、1〜2日遅れで影響が現れる。

【FOMC イベント研究】
FOMC会合前後で株価に有意な差なし（p = 0.897）。
個別のFOMC会合の影響は一貫していない。
```

---

##  ETLパイプライン

### データフロー

```
【Extract（抽出）】
yfinance API → 日経225の日足データ（7年分, 1700+行）
    ↓
【Transform（変換）】
SQLite → Window関数で移動平均計算 → 月次集計テーブル作成
    ↓
【Load（活用）】
Python → クロスオーバーシグナル生成 → t検定で有意性判定
    ↓
【自動化】
AWS S3 へアップロード → Lambda で定期実行（設計済み）
```

### SQL での計算例

Window関数を使った移動平均の計算：

```sql
SELECT
    date,
    close,
    AVG(close) OVER (
        ORDER BY date
        ROWS BETWEEN 19 PRECEDING AND CURRENT ROW
    ) as ma_20
FROM raw_nikkei225;
```

LAG関数を使ったクロスオーバーシグナル検出：

```sql
SELECT date, close,
    CASE
        WHEN ma_20 > ma_200
             AND LAG(ma_20) OVER (ORDER BY date)
                 <= LAG(ma_200) OVER (ORDER BY date)
        THEN 'BUY'
        WHEN ma_20 < ma_200
             AND LAG(ma_20) OVER (ORDER BY date)
                 >= LAG(ma_200) OVER (ORDER BY date)
        THEN 'SELL'
    END as signal
FROM with_moving_avg;
```

---

---

## ⏰ ワークフロー（Airflowスタイル DAG）

Extract（データ取得, 8.4秒）
↓
Transform（SQL加工, 0.1秒）
↓
┌─────┴─────┐
↓           ↓
Quality     Analysis
（品質テスト） （統計分析）
↓           ↓
└─────┬─────┘
↓
Report（レポート出力）
総実行時間: 約12秒（ボトルネックはExtract = 外部API通信）

---

## 🧪 テスト + CI/CD

### テスト戦略

| レベル | ツール | テスト数 | 内容 |
|---|---|---|---|
| ユニットテスト | pytest | 12件 | DB操作、SQL変換、データ品質 |
| データ品質テスト | Python + SQL | 6〜9件 | NULL、重複、範囲、フォーマット |
| 統合テスト | Workflow Engine | 6ステップ | パイプライン全体の動作確認 |
| CI/CD | GitHub Actions | 自動 | push時に全テスト自動実行 |

---

## 📊 パフォーマンス

| 処理 | 実行時間 | 備考 |
|---|---|---|
| Extract (yfinance) | 8.4秒 | 外部API通信がボトルネック |
| Transform (SQL) | 0.1秒 | raw→staging→intermediate |
| Quality Check | 0.02秒 | 6項目自動テスト |
| Analysis | 0.05秒 | シグナル生成 + t検定 |
| Granger | 3.0秒 | 因果推論（外部データ取得含む） |
| Total | 11.6秒 | 1,772行 × 7年分 |

## 実行方法

### 方法1：ローカルでJupyter分析

```bash
git clone https://github.com/dendencode/nikkei225-analysis.git
cd nikkei225-analysis
pip install -r requirements.txt
jupyter notebook
```

### 方法2：ETLパイプラインを実行

```bash
python src/etl.py
```

### 方法3：Dockerで実行（環境不要）

```bash
docker build -t nikkei225 .
docker run nikkei225
```

### 方法4：AWS S3連携（要AWSアカウント）

```bash
pip install boto3 awscli
aws configure
python src/s3_integration.py

# AWS未設定でも動作確認可能
python src/s3_integration.py --dry-run
```
### 方法5：docker-compose（ETL + Jupyter）

```bash
docker-compose -f infrastructure/docker-compose.yml run etl
docker-compose -f infrastructure/docker-compose.yml up jupyter
```

### 方法6：テスト実行

```bash
python -m pytest tests/ -v
```

---

##  技術スタック

```
分析:          Python, pandas, numpy, scipy, statsmodels
可視化:        matplotlib, seaborn
データベース:  SQLite（Window関数, JOIN, サブクエリ, CASE, インデックス）
テーブル設計:  正規化（Dimension/Fact）, Star Schema
データ取得:    yfinance
ETL:           Python スクリプト + dbtスタイル層構造
ワークフロー:  Airflowスタイル DAG + リトライ + ログ
コンテナ化:    Docker, docker-compose
クラウド:      AWS S3, Lambda（設計済み）
テスト:        pytest（12件）
CI/CD:         GitHub Actions
バージョン管理: Git / GitHub
```

---

##  今後の拡張予定

- dbt でデータ変換パイプラインを構築（raw → intermediate → marts）
- Airflow で毎日自動実行を実装
- BigQuery / Snowflake への移行検討
- MLflow でモデル管理 + 機械学習による価格予測

---

##  ライセンス

MIT License

---

実装期間: 2週間