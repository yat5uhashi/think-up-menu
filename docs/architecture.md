# 設計方針（アーキテクチャ）

献立提案アプリのバックエンドの設計ルール。**REST API（Django REST Framework）+ サービス層パターン**を採用する。

## 基本方針

- **API ファースト**：画面は持たず、JSON を返す REST API として実装する（フロントエンドは別）。
- **薄い View・厚いサービス**：ビジネスロジックは View や Serializer ではなく `services` / `selectors` に置く。
- **1機能 = 1アプリ**にこだわらず、まずは `app` 内に役割別ファイルで分割する。規模が大きくなったらアプリを分割する。

## レイヤー構成

```
リクエスト
   │
   ▼
[ View (views.py) ]        ← 入出力のみ。認証・リクエスト解釈・レスポンス整形
   │  └ Serializer (serializers.py) で入力検証・出力変換
   ▼
[ Service / Selector ]     ← ビジネスロジックの本体
   │   services.py  : 書き込み・更新・複雑な処理（献立を提案する 等）
   │   selectors.py : 読み取り専用クエリ（レシピ一覧を取得する 等）
   ▼
[ Model (models.py) ]      ← データ定義と、そのモデル単体で完結する振る舞い
   │
   ▼
データベース (PostgreSQL)
```

### 各レイヤーの責務

| レイヤー | ファイル | やること | やらないこと |
|---|---|---|---|
| View | `views.py` | リクエスト受付、サービス呼び出し、レスポンス返却 | ビジネスロジック、複雑なクエリ |
| Serializer | `serializers.py` | 入力のバリデーション、出力のJSON変換 | DB更新、ビジネスロジック |
| Service | `services.py` | 書き込み系ロジック、複数モデルの調整、トランザクション | HTTPの知識（request/response） |
| Selector | `selectors.py` | 読み取り系クエリの組み立て | 書き込み |
| Model | `models.py` | フィールド定義、制約、単一モデルで閉じるメソッド | 他モデルをまたぐ処理（→service） |

### 守るべきルール

1. **View からモデルを直接 `.save()` / 複雑な `.filter()` しない。** 書き込みは service、読み取りは selector を経由する。
2. **service / selector は `request` を引数に取らない。** 必要な値（ログインユーザー等）は呼び出し側が取り出して渡す。これでテストが純粋な関数テストになる。
3. **トランザクションは service 層で張る**（`@transaction.atomic`）。
4. **例外はドメイン例外を投げ、View 層で HTTP ステータスに変換する**（例：`django.core.exceptions.ValidationError` → 400）。

## ディレクトリ構成（app）

```
app/
├── models.py        # ORM モデル
├── serializers.py   # DRF シリアライザ
├── services.py      # 書き込み系ビジネスロジック
├── selectors.py     # 読み取り系クエリ
├── views.py         # DRF ビュー（薄く保つ）
├── urls.py          # ルーティング
├── admin.py         # 管理画面登録
├── apps.py
├── migrations/
└── tests/           # テスト（後述）
    ├── test_services.py
    ├── test_selectors.py
    └── test_api.py
```

## テスト方針

- **service / selector を最優先でテストする**（ロジックがここに集まるため）。
- API は正常系1本＋認証/バリデーションの異常系をカバー。
- `pytest` ではなく Django 標準の `manage.py test`（`django.test.TestCase`）から始める。必要になれば pytest 導入を検討。

## 将来の拡張メモ

- 機能ドメインが増えたら `app` を `recipes` / `menus` / `accounts` 等のアプリに分割。
- 認証を本格化する場合は `djangorestframework-simplejwt`（JWT）の導入を検討。
- API ドキュメントが必要になれば `drf-spectacular`（OpenAPI）を導入。
