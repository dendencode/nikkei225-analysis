# 日経225 データ分析ポートフォリオ

##  目的
統計的根拠を持つデータ分析を実装し、記録を残す。

##  実装内容

### 分析ノートブック
- Notebook 1 - データ取得 + 基本統計量 + 可視化
- Notebook 2 - 移動平均戦略 + バックテスト + t検定による有意性検証
- Notebook 3 - 因果推論（Granger因果性テスト + イベント研究）

### 主な分析結果
- 移動平均クロスオーバー戦略：平均リターン +2.07%（ただしp=0.68で統計的に有意ではない）
- Granger因果性テスト：金利変化 → 翌日の株価変動に有意な因果関係あり（p=0.024）
- FOMC イベント研究：会合前後で有意な差は認められず（p=0.897）

##  技術スタック
- Python (pandas, numpy, scipy, statsmodels)
- yfinance（データ取得）
- matplotlib / seaborn（可視化）

##  進捗
- [x] テクニカル分析 + t検定
- [x] 因果推論（Granger テスト）
- [ ] SQL データ管理（Day 3-4）
- [ ] Docker 環境構築（Day 5）
- [ ] AWS 連携（Day 6）

##  実行方法
```bash
pip install -r requirements.txt
jupyter notebook
```