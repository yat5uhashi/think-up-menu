# syntax=docker/dockerfile:1

# uv の公式イメージから uv バイナリを取得（バージョンは .python-version と揃える）
FROM ghcr.io/astral-sh/uv:0.11.21 AS uv

FROM python:3.13-slim

# uv をコピーして利用（イメージ内でも同じツールでビルドする）
COPY --from=uv /uv /uvx /bin/

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/usr/local

WORKDIR /code

# 依存だけ先にインストールしてレイヤキャッシュを効かせる
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-install-project --no-dev

# アプリ本体
COPY . .

EXPOSE 8000

# 開発用のデフォルト起動（本番は docker-compose で gunicorn に差し替え）
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
