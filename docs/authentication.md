# 認証設計

## 方針

- **JWT（JSON Web Token）認証**を採用（`djangorestframework-simplejwt`）。スマホ/SPA などステートレスなクライアントと相性が良い。
- admin・ブラウザブルAPI 用に **Session 認証も併用**（[settings.py](../config/settings.py) の `DEFAULT_AUTHENTICATION_CLASSES`）。
- デフォルトは **認証必須**（`IsAuthenticated`）。公開エンドポイントだけ個別に `AllowAny` を付ける。

## トークンの種類と寿命

| トークン | 用途 | 寿命 |
|---|---|---|
| access | API 呼び出し時に毎回送る | 30分 |
| refresh | access の再発行に使う | 14日 |

設定は `SIMPLE_JWT`（[settings.py](../config/settings.py)）。

## エンドポイント

| メソッド | URL | 説明 |
|---|---|---|
| POST | `/api/v1/auth/token/` | username/password → access + refresh を発行 |
| POST | `/api/v1/auth/token/refresh/` | refresh → 新しい access を発行 |
| POST | `/api/v1/auth/token/verify/` | トークンの有効性を検証 |

### 使い方

```bash
# 1. トークン取得
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "pass12345"}'
# => {"access": "...", "refresh": "..."}

# 2. access トークンを Authorization ヘッダに付けて API を叩く
curl http://localhost:8000/api/v1/recipes/ \
  -H "Authorization: Bearer <access>"

# 3. access が切れたら refresh で再発行
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<refresh>"}'
```

## ルール

- **access トークンの寿命は短く保つ**（漏洩時の被害を抑える）。長期保持は refresh 側で。
- クライアントは **refresh トークンを安全に保管**する（モバイルはセキュアストレージ等）。
- 認証はビューに任せ、services / selectors は「認証済みの user」を引数で受け取る（[architecture.md](architecture.md)）。

## 将来の拡張メモ

- ログアウト（トークン無効化）が必要になれば `ROTATE_REFRESH_TOKENS` + `token_blacklist` アプリを有効化する。
- ソーシャルログインが必要なら `dj-rest-auth` / `django-allauth` を検討。
- ユーザーモデルを拡張する可能性があるなら、早い段階でカスタムユーザーモデルへの移行を検討する。
