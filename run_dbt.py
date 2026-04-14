"""
dbt 実行用ヘルパー

使い方:
  python run_dbt.py init
  python run_dbt.py run
  python run_dbt.py test
  python run_dbt.py docs generate
"""
import sys
from dbt.cli.main import cli

if __name__ == "__main__":
    cli()