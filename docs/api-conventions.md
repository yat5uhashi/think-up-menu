# API 規約（URL・バージョニング）

## バージョニング

- **URL パスにバージョンを含める**：`/api/v1/...`（`URLPathVersioning`）。
- 許可バージョンは [settings.py](../config/settings.py) の `ALLOWED_VERSIONS` で管理。範囲外（例 `/api/v2/`）は 404。
- 破壊的変更が必要になったら `v2` を**並行提供**し、`v1` は段階的に廃止する。

## リソースの分類（どこに置くか）

エンドポイントは役割で3つに分ける。**「認証アクション」と「ドメイン資源」を混ぜない**。

| 分類 | パス | 内容 | 例 |
|---|---|---|---|
| 認証アクション | `/api/v1/auth/...` | ログイン・トークン・登録・パスワード等 | `auth/token/`, `auth/register/`, `auth/logout/` |
| 自分のアカウント | `/api/v1/auth/me/` | ログイン中ユーザー自身の情報（identity） | GET/PATCH |
| ドメイン資源 | `/api/v1/<resource>/` | アプリのデータ。独立したトップレベル資源 | `ingredients/`, `menus/`, `favorites/` |

- **ドメイン資源は `auth` の下に置かない**。「ログイン中ユーザーに紐づく」ことは `auth` 配下にする理由にならない。
- **ユーザーへの紐付けは URL ではなく `request.user` で行う**（`/users/{id}/favorites/` のように他人の id を URL に晒さない）。これが「自分の資源だけ返す」＝水平権限昇格の防止になる。

## URL 設計

- **リソースは複数形の名詞**：`/api/v1/ingredients/`、`/api/v1/menus/`。
- 階層は浅く保つ。ネストは1段まで：`/api/v1/menus/{id}/ingredients/`。
- 動詞は URL に入れない（操作は HTTP メソッドで表現）。やむを得ないアクションは末尾に：`/api/v1/menus/{id}/favorite/`。
- 末尾スラッシュあり（Django のデフォルト）。

| 操作 | メソッド | URL | 成功ステータス |
|---|---|---|---|
| 一覧取得 | GET | `/api/v1/recipes/` | 200 |
| 1件取得 | GET | `/api/v1/recipes/{id}/` | 200 |
| 作成 | POST | `/api/v1/recipes/` | 201 |
| 全更新 | PUT | `/api/v1/recipes/{id}/` | 200 |
| 部分更新 | PATCH | `/api/v1/recipes/{id}/` | 200 |
| 削除 | DELETE | `/api/v1/recipes/{id}/` | 204 |

## リクエスト / レスポンス

- 形式は **JSON** に統一。
- フィールド名は **snake_case**。
- 一覧はページネーション（`PAGE_SIZE=20`）。`?page=2` で取得。
- 日時は **ISO 8601 / UTC**（`USE_TZ=True`）。

### 命名

- クエリパラメータも snake_case：`?keyword=...&is_active=true`。
- 絞り込み・並び替え・検索はクエリパラメータで表現する。

## エラー

- エラーレスポンスは全 API 共通フォーマット（[error-handling.md](error-handling.md)）：

  ```json
  { "error": { "code": "...", "message": "...", "details": {} } }
  ```

## 認証

- 認証は JWT（`Authorization: Bearer <access>`）。詳細は [authentication.md](authentication.md)。
- デフォルト認証必須。公開エンドポイントのみ個別に許可する。
