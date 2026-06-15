# think-up-menu（献立提案アプリ）

献立提案アプリのバックエンド。Python 3.13 + Django 5.2 (LTS) + PostgreSQL。Python は **uv** でプロジェクトごとにバージョン管理しています。

## 構成

| 項目 | 内容 |
|---|---|
| Python | 3.13（`.python-version` で固定。uv が自動取得） |
| Web | Django 5.2.15 + Django REST Framework（REST API） |
| DB | PostgreSQL 17（Docker） |
| パッケージ管理 | uv（`pyproject.toml` / `uv.lock`） |
| Lint / Format | ruff |

## 開発ルール（最初に読む）

- **設計方針**：[docs/architecture.md](docs/architecture.md) — REST API + サービス層パターン
- **コーディング規約**：[docs/coding-style.md](docs/coding-style.md) — PEP8 / ruff / 命名 / コミット規約
- **ログ設計**：[docs/logging.md](docs/logging.md) — stdout 出力・dev=text/prod=json
- **エラー設計**：[docs/error-handling.md](docs/error-handling.md) — ドメイン例外・統一エラーレスポンス
- **ディレクトリ設計**：[docs/directory.md](docs/directory.md) — 役割分担とアプリ分割方針
- **認証設計**：[docs/authentication.md](docs/authentication.md) — JWT（simplejwt）
- **API規約**：[docs/api-conventions.md](docs/api-conventions.md) — URL設計・バージョニング（/api/v1/）
- **テスト方針**：[docs/testing.md](docs/testing.md) — pytest
- **CI**：[docs/ci.md](docs/ci.md) — GitHub Actions（テスト+Lint。デプロイは後日）
- **ブランチ運用**：[docs/branching.md](docs/branching.md) — main + feature/fix・PR運用

要点だけ:
- ビジネスロジックは View ではなく `services.py`（書き込み）/ `selectors.py`（読み取り）に置く。
- 例外はドメイン例外（`core/exceptions.py`）を投げ、View では捕まえない（変換は `core` の例外ハンドラに集約）。
- ログは `logging.getLogger(__name__)` を使い `print()` は使わない。秘密情報は出さない。
- 認証は JWT（`Authorization: Bearer <token>`）。API は `/api/v1/` 配下。
- push 前に `uv run ruff format .` → `uv run ruff check --fix .` → `uv run pytest`。
- `main` に直接 push しない。`feature/` か `fix/` ブランチ → PR 経由。
- シークレットは `.env` 経由（コミットしない）。

### 開発フロー（仕様駆動 + DDDライト）

機能追加は「仕様 → 実装 → レビュー」の順で進める。Claude Code のカスタムコマンドを用意:

| コマンド | 役割 |
|---|---|
| `/spec <機能>` | 仕様書を `docs/specs/<機能>.md` に作成（テンプレ: [docs/specs/_template.md](docs/specs/_template.md)） |
| `/implement <機能>` | 確定した仕様に従い、規約どおりに実装（feature ブランチ + テスト + 品質ゲート） |
| `/code-review` | 変更のレビュー（組込みスキル） |

- 仕様は実装前に確定させる（迷いは仕様段階で潰す）。
- モデリングは DDDライト：ユビキタス言語とドメインモデルを仕様に明記し、サービス層で表現する。

### ディレクトリ構成（概要）

```
think-up-menu/
├── config/          # プロジェクト設定（settings, urls, wsgi）
├── core/            # 共通コード（例外・例外ハンドラ・ログ）。モデルは持たない
├── app/             # 機能アプリ（models/serializers/services/selectors/views/urls）
├── docs/            # 設計・規約ドキュメント
├── Dockerfile / docker-compose.yml
└── pyproject.toml   # 依存・ruff 設定
```

詳細なディレクトリ設計は [docs/directory.md](docs/directory.md) を参照。

## ローカル開発（uv のみ・SQLite）

DB サーバ不要で素早く動かす場合。`DB_HOST` が未設定だと自動で SQLite になります。

```powershell
uv run python manage.py migrate
uv run python manage.py runserver
```

パッケージ追加・削除:

```powershell
uv add <package>        # 追加（uv.lock も更新）
uv remove <package>     # 削除
uv sync                 # lock に合わせて環境を同期
```

Python バージョンを変える:

```powershell
uv python pin 3.12      # .python-version を書き換え
uv sync
```

## Docker 開発（Django + PostgreSQL）

`.env` の値で起動します（秘密情報なので git 管理対象外）。

```powershell
docker compose up -d --build      # 起動
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose logs -f web        # ログ
docker compose down               # 停止
docker compose down -v            # 停止＋DBデータ削除
```

- アプリ: http://localhost:8000/
- ソースはマウント済みで、コード変更は自動リロードされます。

## 本番向けメモ

- `.env` の `DJANGO_SECRET_KEY` を必ず変更し、`DJANGO_DEBUG=False` にする。
- 本番は runserver ではなく `gunicorn config.wsgi`（導入済み）を使う。
- `python manage.py collectstatic` で `staticfiles/` に集約。
