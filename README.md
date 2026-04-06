# 日経225 データ分析ポートフォリオ

[![Python](https://img.shields.io/badge/Python-3.11-blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Containerized-2496ED)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## プロジェクト概要

日経225の過去7年分のデータを使い、統計的根拠を持つデータ分析とETLパイプライン + クラウド自動化を実装したポートフォリオです。

「なんとなく分析」ではなく、統計検定（t検定）で戦略の有意性を検証し、Granger因果性テストで因果関係を証明するなど、科学的な根拠に基づく分析を重視しています。

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
| SQL | Window関数で移動平均計算、サブクエリ、CASE文 | データウェアハウスでの加工 |
| ETLパイプライン | etl.py で Extract→Transform→Load を自動化 | 本番環境での定期実行 |
| Docker | コンテナ化で環境を完全再現 | チーム開発での環境統一 |
| AWS設計 | S3連携 + Lambda定期実行のアーキテクチャ | サーバーレス分析基盤 |

---

##  プロジェクト構成

```
nikkei225-analysis/
├── notebooks/
│   ├── 1_data_acquisition.ipynb        # データ取得 + 基本統計
│   ├── 2_technical_analysis.ipynb      # 移動平均 + バックテスト + t検定
│   ├── 3_causal_inference.ipynb        # 因果推論（Granger + イベント研究）
│   ├── 4_data_preparation_sql.ipynb    # SQL基礎（テーブル設計 + クエリ）
│   └── 5_sql_advanced.ipynb            # SQL応用（Window関数 + ETL連携）
│
├── src/
│   ├── etl.py                          # ETLパイプライン
│   └── s3_integration.py              # AWS S3 連携
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
ラグ1（翌日）: p = 0.024 ✓ 有意
ラグ2〜5:      p > 0.05   有意ではない

【結論】
金利変化は「翌日の」株価変動を予測する力がある（p < 0.05）。
同じ日には反応しないが、1日遅れで影響が現れる。

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

---

##  技術スタック

```
分析:          Python, pandas, numpy, scipy, statsmodels
可視化:        matplotlib, seaborn
データベース:  SQLite（Window関数, サブクエリ, CASE文, JOIN）
データ取得:    yfinance
ETL:           Python スクリプト（Extract → Transform → Load）
コンテナ化:    Docker
クラウド:      AWS S3, Lambda（設計済み）
バージョン管理: Git / GitHub
```

---

##  今後の拡張予定

- dbt でデータ変換パイプラインを構築（raw → intermediate → marts）
- Airflow で毎日自動実行を実装
- GitHub Actions で CI/CD パイプライン（自動テスト + デプロイ）
- BigQuery / Snowflake への移行検討

---

##  ライセンス

MIT License

---

実装期間: 2週間（継続開発中）