# コーディング規約

基本は **PEP 8** に準拠し、整形と静的チェックは **ruff** に任せる（手動で細かく気にしない）。設定は [pyproject.toml](../pyproject.toml) の `[tool.ruff]` を参照。

## ツール

| 目的 | コマンド |
|---|---|
| 整形（フォーマット） | `uv run ruff format .` |
| Lint チェック | `uv run ruff check .` |
| Lint 自動修正 | `uv run ruff check --fix .` |

> コミット前に `ruff format` と `ruff check --fix` を実行する習慣にする。

## スタイルの要点

- **行長**：最大 100 文字。
- **クォート**：文字列はダブルクォート `"..."` に統一（ruff format が自動変換）。
- **import 順**：標準ライブラリ → サードパーティ → 自作、の3グループ（ruff の `I` ルールが自動整列）。
- **インデント**：スペース4。タブ禁止。
- **f-string** を優先（`%` や `.format()` より）。

## 命名規約

| 対象 | 規約 | 例 |
|---|---|---|
| 変数・関数 | `snake_case` | `suggest_menu`, `recipe_count` |
| クラス | `PascalCase` | `Recipe`, `MenuSuggestService` |
| 定数 | `UPPER_SNAKE_CASE` | `MAX_INGREDIENTS` |
| モデル | 単数形・`PascalCase` | `Recipe`（テーブルは複数形でOK） |
| サービス関数 | `動詞_目的語` | `create_recipe`, `suggest_menu_for_user` |
| selector 関数 | `get_` / `list_` 始まり | `get_recipe`, `list_recipes` |
| ブール変数 | `is_` / `has_` 始まり | `is_active`, `has_allergy` |

## 型ヒント

- 新規に書く関数には**できる範囲で型ヒントを付ける**（特に service / selector の引数・戻り値）。
- 厳密な型チェッカ（mypy 等）は当面導入しない。読みやすさ目的。

```python
def list_recipes(*, user: User, keyword: str | None = None) -> QuerySet[Recipe]:
    ...
```

## docstring / コメント

**様式は Google スタイル・日本語**。ruff の pydocstyle（`D` ルール, `convention = "google"`）で自動チェックする（設定は [pyproject.toml](../pyproject.toml)）。

### 必須範囲（バランス型）

| 対象 | docstring |
|---|---|
| 公開モジュール | 必須（意味のあるモジュール。空スタブも1行で可） |
| 公開クラス | 必須 |
| 公開関数（services/selectors 等） | **必須**（最重要） |
| メソッド（View の post 等のオーバーライド） | 任意（クラスの docstring で説明できれば省略可） |
| マジックメソッド / `__init__` / Django の `Meta`・`AppConfig` | 任意 |
| テスト・`manage.py` | 不要（チェック対象外） |

### 書き方

- **1行要約**から書く。引数・戻り値・例外が自明でなければ `Args:` / `Returns:` / `Raises:` を足す。

```python
def list_recipes(*, keyword: str | None = None) -> QuerySet[Recipe]:
    """レシピ一覧を返す。

    Args:
        keyword: 指定時は名前で部分一致絞り込み。

    Returns:
        条件に合致するレシピの QuerySet。
    """
    ...
```

- 末尾の句点（。）有無やピリオド要否は強制しない（日本語前提のため `D400/D401/D415` は無効）。
- コメントは「なぜそうするか（why）」を書く。「何をしているか（what）」はコードで表現する。

## Django / DRF の約束

- **Fat View 禁止**：ロジックは service / selector へ（[architecture.md](architecture.md) 参照）。
- **マイグレーションは必ずコミット**する。`makemigrations` の結果をレビュー対象に含める。
- **シークレットはコードに書かない**。`os.environ` 経由（`.env`）で読む。`.env` はコミットしない。
- ビューは原則 **DRF の `APIView` / `ViewSet`** を使い、素の Django View は使わない。

## Git コミット規約

- **1コミット1論点**。意味のある単位で小さくコミットする。
- メッセージは**命令形・簡潔に**。日本語可。プレフィックスを付けると分かりやすい：

  | プレフィックス | 用途 |
  |---|---|
  | `feat:` | 新機能 |
  | `fix:` | バグ修正 |
  | `refactor:` | 挙動を変えない整理 |
  | `docs:` | ドキュメント |
  | `test:` | テスト追加・修正 |
  | `chore:` | 設定・依存更新など |

  例：`feat: 献立提案APIを追加`

- **`main` に直接 push しない**。`feature/` または `fix/` ブランチ → Pull Request 経由で入れる。詳細は [branching.md](branching.md)。
