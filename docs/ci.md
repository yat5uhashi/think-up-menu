# CI 設計

## 方針

- **CI はテストと静的チェックのみ**。デプロイ（CD）はインフラ整備後に別途追加する。
- GitHub Actions を使用（[.github/workflows/ci.yml](../.github/workflows/ci.yml)）。

## トリガー

- `main` への push
- すべての Pull Request

## 実行内容（test ジョブ）

| ステップ | 内容 |
|---|---|
| Lint | `uv run ruff check .` |
| Format チェック | `uv run ruff format --check .`（未整形なら失敗） |
| テスト | `uv run pytest` |

- Python 3.13 を uv でセットアップし、`uv sync --frozen`（ロック厳守）で依存をインストール。
- テスト用に **PostgreSQL 17 のサービスコンテナ**を起動し、`DB_HOST=localhost` で接続。
- 秘密値はダミー（`DJANGO_SECRET_KEY: ci-test-secret-key`）。本番のシークレットは使わない。

## ローカルで同じチェックを通すには

push 前に以下を実行しておくと CI で落ちにくい：

```powershell
uv run ruff format .
uv run ruff check --fix .
uv run pytest
```

## 将来の拡張（インフラ整備後）

- `deploy` ジョブを追加し、`main` への push 成功時にデプロイ。
- イメージビルド（Dockerfile）→ レジストリ push → 本番反映、の流れを想定。
- マイグレーション適用ステップ、ヘルスチェックを組み込む。
- 必要に応じて `pytest-cov` でカバレッジ計測・閾値チェックを追加。
