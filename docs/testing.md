# テスト方針

## 方針

- **pytest + pytest-django** を使う（設定は [pyproject.toml](../pyproject.toml) の `[tool.pytest.ini_options]`）。
- **テスト対象の優先順位**：
  1. `services.py` / `selectors.py`（ロジックの本体。最優先）
  2. API（正常系1本＋認証/バリデーションの異常系）
  3. モデルのカスタムメソッド・制約
- **薄い View・厚いサービス**なので、ロジックの単体テストが中心になる（[architecture.md](architecture.md)）。

## 実行

```powershell
uv run pytest                 # 全テスト
uv run pytest app/tests/test_auth.py   # ファイル指定
uv run pytest -k token        # 名前で絞り込み
uv run pytest -q              # 簡潔表示
```

- 2回目以降は `--reuse-db`（既定で有効）でテストDBを再利用して高速化。
- モデルを変更してテストDBを作り直したいときは `uv run pytest --create-db`。

## 置き場所と命名

```
app/tests/
├── __init__.py
├── test_services.py    # サービス層
├── test_selectors.py   # セレクタ層
└── test_api.py         # API（エンドポイント）
```

- ファイル名は `test_*.py`、関数名は `test_*`。
- DB を使うテストには `@pytest.mark.django_db` を付ける。

## 書き方の指針

```python
import pytest


@pytest.mark.django_db
def test_create_recipe_saves_to_db():
    # Arrange（準備） → Act（実行） → Assert（検証）の3段で書く
    recipe = create_recipe(name="カレー")
    assert recipe.id is not None
```

- **1テスト1検証の観点**。何を確かめているかが名前で分かるようにする。
- 外部依存（外部API・時刻・乱数）は**モック/固定**してテストを安定させる。
- 異常系（権限なし・バリデーションエラー・404）も必ず1本は書く。
- API テストは `rest_framework.test.APIClient` を使う。認証が要るものは
  `client.force_authenticate(user=...)` でログイン状態を作る。

## カバレッジ

- 当面はカバレッジ率の数値目標は設けない（重要なロジックを確実にテストする方を優先）。
- 必要になれば `pytest-cov` を導入して計測する。

## CI

- push / Pull Request で GitHub Actions が自動でテストを実行する（[ci.md](ci.md)）。
