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

## 検証はどの層で行うか

| 層 | 役割 | 違反したときの応答 |
|---|---|---|
| **シリアライザ（View 層）** | **クライアント入力の検証**。必須・形式・最大長・業務ルール | **400** `validation_error` |
| サービス層 | 業務ルール違反（ドメイン例外） | **400**（`core.exceptions` のステータス） |
| **DB 制約** | **不変条件**（`unique` / `NOT NULL` / `CheckConstraint` / `varchar(n)`） | **500**（下記） |

**モデル層では `full_clean()` を呼ばない**。Django の設計思想どおり「モデルは DB への薄いマッピング、検証はシリアライザ層」を守る（Django 本体の `UserManager` も `full_clean()` を呼ばない）。

### DB 制約違反を 400 に変換しない理由

クライアント入力の検証は **シリアライザが済ませている前提**なので、そこをすり抜けて DB 制約に到達するということは、**検証層とモデル定義が食い違っている＝サーバー側の不具合**を意味する。

これを 400 に変換すると、**サーバーのバグをクライアントのせいにして隠蔽**してしまう。したがって:

- `IntegrityError` / `DataError` は**マッピングしない**。「想定外の例外」として扱う。
- 例外ハンドラの分岐3が `logger.exception` で記録し、**500** を返す（`DEBUG=False` では中身を漏らさない）。
- 4xx はクライアントの誤り、5xx はサーバーの誤り、という区別を守る。

### 不変条件は DB 制約で守る

`blank=False` はフォーム/シリアライザ層の制約にすぎず、ORM から直接 `save()` すると空文字が保存できてしまう。**本当に守りたい不変条件は DB 制約にする**。

```python
class Meta(AbstractUser.Meta):
    constraints = [
        models.CheckConstraint(
            condition=~models.Q(display_name=""),
            name="accounts_user_display_name_not_empty",
        ),
    ]
```

## 原則

- **想定済みのエラーは必ずドメイン例外**にする（裸の `Exception` を投げない）。
- View では例外を**捕まえない**（ハンドラに任せる）。捕まえるのは「捕まえて回復できるとき」だけ。
- 4xx はユーザーに原因が分かるメッセージを返す。5xx は詳細を返さずログに残す。
- **サーバー側の不整合を 4xx に丸めない**（バグを隠さない）。
