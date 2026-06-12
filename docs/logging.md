# ログ設計

## 方針

- **出力先は常に標準出力（stdout）**。ファイルには書かない（コンテナ運用の定石／12-factor）。集約は基盤側（Docker ログ・クラウドのログ収集）に任せる。
- **形式は環境で切替**：
  - 開発 = `text`（人が読める1行）
  - 本番 = `json`（構造化。ログ集約・検索向け）
- 切替は環境変数で行う（[settings.py](../config/settings.py) の `LOGGING`）：

  | 環境変数 | 値 | 既定 |
  |---|---|---|
  | `DJANGO_LOG_FORMAT` | `text` / `json` | `text` |
  | `DJANGO_LOG_LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` | `INFO` |

## 使い方

各モジュールの先頭でロガーを取得する（**ロガー名はモジュール名固定**）：

```python
import logging

logger = logging.getLogger(__name__)


def suggest_menu(*, user):
    logger.info("献立提案を開始", extra={"user_id": user.id})
    ...
    logger.info("献立提案が完了", extra={"user_id": user.id, "count": len(result)})
```

- `extra={...}` に渡したキーは **JSON ログでは各フィールドとして出力**される（検索しやすい）。
- 文字列連結ではなく**遅延フォーマット**を使う：`logger.info("user %s", user.id)`（`f"..."` で組み立てない）。

## ログレベルの使い分け

| レベル | 用途 | 例 |
|---|---|---|
| `DEBUG` | 開発時の詳細。本番では出さない | クエリ条件、分岐の値 |
| `INFO` | 正常系の重要イベント | 「献立提案を完了」「レシピを作成」 |
| `WARNING` | 異常ではないが注意したいこと | リトライ発生、非推奨APIの利用 |
| `ERROR` | 処理が失敗した | 外部API呼び出し失敗、500系エラー |

> 4xx のユーザー起因エラー（バリデーション等）は基本 `INFO`。サーバー起因（5xx）は `ERROR` で `exc_info` を付ける。例外ハンドラの方針は [error-handling.md](error-handling.md) を参照。

## やってはいけないこと

- **個人情報・秘密情報をログに出さない**（パスワード、トークン、メール本文など）。
- View で `print()` を使わない。必ず logger を使う。
- 例外を握りつぶして無言で続行しない。最低でも `logger.exception(...)` を残す。
