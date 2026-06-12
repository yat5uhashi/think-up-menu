# Project

Python 3.13 + Django 5.2 (LTS) + PostgreSQL。Python は **uv** でプロジェクトごとにバージョン管理しています。

## 構成

| 項目 | 内容 |
|---|---|
| Python | 3.13（`.python-version` で固定。uv が自動取得） |
| Web | Django 5.2.15 |
| DB | PostgreSQL 17（Docker） |
| パッケージ管理 | uv（`pyproject.toml` / `uv.lock`） |

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
