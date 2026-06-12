# エラー設計

## 方針

- **ロジック層（services / selectors）はドメイン例外を投げる**。HTTP ステータスコードを意識しない。
- **HTTP への変換は1か所に集約**する（[core/exception_handlers.py](../core/exception_handlers.py)）。View で個別に try/except しない。
- **エラーレスポンスは全 API で統一フォーマット**。フロントエンドが一貫して扱える。

## エラーレスポンスの形

```json
{
  "error": {
    "code": "validation_error",
    "message": "入力内容が正しくありません。",
    "details": {
      "name": ["この項目は必須です。"]
    }
  }
}
```

| フィールド | 説明 |
|---|---|
| `code` | 機械可読なエラーコード（分岐に使う）。例: `not_found`, `validation_error` |
| `message` | 利用者向けの日本語メッセージ |
| `details` | 任意。フィールド別エラーなどの補足（無い場合は省略） |

## ドメイン例外

[core/exceptions.py](../core/exceptions.py) に定義。services / selectors からはこれを投げる。

| 例外 | HTTP | code |
|---|---|---|
| `ApplicationError` | 400 | `error` | （基底） |
| `ValidationError` | 400 | `validation_error` |
| `NotFoundError` | 404 | `not_found` |
| `PermissionDeniedError` | 403 | `permission_denied` |
| `ConflictError` | 409 | `conflict` |

使用例：

```python
from core.exceptions import NotFoundError

def get_recipe(*, recipe_id: int) -> Recipe:
    try:
        return Recipe.objects.get(id=recipe_id)
    except Recipe.DoesNotExist as e:
        raise NotFoundError("レシピが見つかりません。", code="recipe_not_found") from e
```

独自のコードを足したいときは `code=` と必要なら `details=` を渡す。新しい例外型が必要なら `ApplicationError` を継承して追加する。

## 変換の流れ（exception_handler）

1. **ドメイン例外（`ApplicationError`）** → `status_code` と `code`/`message`/`details` を使ってそのまま整形。
2. **DRF 標準例外**（`ValidationError`, `NotFound`, `NotAuthenticated` 等） → DRF 既定処理の結果を統一フォーマットに詰め替え。バリデーションエラーは `details` にフィールド別エラーを入れる。
3. **想定外の例外（500 相当）** → `logger.exception` で記録し、Django 既定の 500 ハンドリングに委ねる（`DEBUG=False` では中身を漏らさない）。

## 原則

- **想定済みのエラーは必ずドメイン例外**にする（裸の `Exception` を投げない）。
- View では例外を**捕まえない**（ハンドラに任せる）。捕まえるのは「捕まえて回復できるとき」だけ。
- 4xx はユーザーに原因が分かるメッセージを返す。5xx は詳細を返さずログに残す。
