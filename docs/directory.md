# ディレクトリ設計

## 全体構成

```
think-up-menu/
├── config/                  # プロジェクト設定（アプリではない）
│   ├── settings.py              # 設定（環境変数で挙動を切替）
│   ├── urls.py                  # ルートの URL 定義
│   ├── wsgi.py / asgi.py        # 起動エントリ
│
├── core/                    # 共通コードアプリ（モデルは持たない）
│   ├── exceptions.py            # ドメイン例外
│   ├── exception_handlers.py    # DRF 例外ハンドラ（→統一エラーレスポンス）
│   ├── logging.py               # JSON ログフォーマッタ
│   └── apps.py
│
├── app/                     # 機能アプリ（献立・レシピ等。当面はここに集約）
│   ├── models.py                # ORM モデル
│   ├── serializers.py           # DRF シリアライザ（入出力）
│   ├── services.py              # 書き込み系ロジック
│   ├── selectors.py             # 読み取り系クエリ
│   ├── views.py                 # DRF ビュー（薄く保つ）
│   ├── urls.py                  # この app の URL
│   ├── admin.py                 # 管理画面登録
│   ├── migrations/              # マイグレーション（コミット対象）
│   └── tests/                   # テスト
│
├── docs/                    # 設計・規約ドキュメント
│   ├── architecture.md          # 設計方針（レイヤー）
│   ├── coding-style.md          # コーディング規約
│   ├── logging.md               # ログ設計
│   ├── error-handling.md        # エラー設計
│   └── directory.md             # このファイル
│
├── Dockerfile               # アプリイメージ
├── docker-compose.yml       # web + db（PostgreSQL）
├── pyproject.toml           # 依存・ruff 設定
├── uv.lock                  # 依存ロック（コミット対象）
├── .python-version          # Python バージョン固定（uv）
├── .env                     # 環境変数（コミットしない）
└── README.md
```

## 役割分担のルール

| 置きたいもの | 置き場所 |
|---|---|
| プロジェクト全体の設定・ルーティング | `config/` |
| 複数アプリで共有する例外・ユーティリティ・基底クラス | `core/` |
| 機能ごとのモデル・API・ロジック | `app/`（将来は機能別アプリに分割） |
| 設計・規約のドキュメント | `docs/` |

## アプリの分割方針

- **当面は単一の `app` に役割別ファイル**で実装する（過度に分割しない）。
- 機能ドメインが増えて `app` が肥大化したら、**機能単位でアプリを分割**する：
  - 例：`recipes/`（レシピ）、`menus/`（献立）、`accounts/`（ユーザー）
  - 分割後も各アプリ内は `models / serializers / services / selectors / views / urls` の構成を踏襲する。
- **共通化したくなったコードは `core/` へ**移す（特定機能に依存しないもの）。

## 命名

- アプリ名・ディレクトリ名は**小文字・複数形**（`recipes`, `menus`）。
- 1ファイル1責務。`services.py` が大きくなったら `services/` パッケージ化して機能別に分割してよい。
