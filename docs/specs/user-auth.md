# 仕様: ユーザー認証（メール+パスワード）

- ステータス: 確定
- 対象バージョン: v1
- 関連ブランチ: `feature/user-auth`

## 1. 概要・目的

献立提案アプリの利用にあたり、ユーザーが**メールアドレスとパスワードで会員登録・ログイン**できるようにする。ログイン状態は JWT で表現し、以降の API 呼び出しを認証する。ソーシャルログインはフェーズ2で追加する（本仕様の対象外）。

## 2. ユビキタス言語（用語定義）

| 用語 | 意味 |
|---|---|
| ユーザー（User） | アプリの利用者。**email を一意な識別子**とする |
| 表示名（display name） | UI 表示用の名前。ログイン識別子ではない |
| 会員登録（register） | 新しいユーザーを作成すること |
| ログイン（login） | 資格情報と引き換えにトークンを発行すること |
| ログアウト（logout） | リフレッシュトークンを無効化すること |
| アクセストークン | API 呼び出しに使う短命トークン（30分） |
| リフレッシュトークン | アクセストークンを再発行するための長命トークン（14日） |

## 3. スコープ

- **やること（フェーズ1）**：
  - 会員登録（email / password / 表示名）
  - ログイン（トークン発行）／トークン更新／トークン検証
  - ログアウト（リフレッシュトークンの無効化）
  - 自分の情報の取得・プロフィール更新（表示名）
  - パスワード変更（ログイン中のユーザー）
- **やらないこと（今回外す）**：
  - メールアドレス確認（verification）→ 登録後すぐ利用可
  - パスワードリセット（メール送信）→ メール基盤整備後（フェーズ2想定）
  - ソーシャルログイン → フェーズ2
  - 退会（アカウント削除）→ 別途仕様化

## 4. ドメインモデル

| 概念 | 主な属性 | 備考 |
|---|---|---|
| User | `email`(一意), `password`(ハッシュ), `display_name`, `is_active`, `is_staff`, `date_joined`, `last_login` | Django の `AbstractUser` ベースのカスタムユーザー。`username` は廃止し `USERNAME_FIELD = "email"` |

- カスタムユーザーモデルは `accounts` アプリに置き、`AUTH_USER_MODEL = "accounts.User"` を設定する。
- **プロジェクト初期に導入する**（後からの変更は困難なため）。dev/test DB は作り直す。

## 5. API 仕様

[api-conventions.md](../api-conventions.md) に従う。すべて `/api/v1/auth/` 配下。

| メソッド | URL | 認証 | 概要 |
|---|---|---|---|
| POST | `/api/v1/auth/register/` | 不要 | 会員登録。成功で 201（ユーザー情報のみ。トークンは返さない） |
| POST | `/api/v1/auth/token/` | 不要 | ログイン。access + refresh を発行 |
| POST | `/api/v1/auth/token/refresh/` | 不要 | refresh → 新しい access |
| POST | `/api/v1/auth/token/verify/` | 不要 | トークンの有効性検証 |
| POST | `/api/v1/auth/logout/` | 要 | refresh トークンを無効化 |
| POST | `/api/v1/auth/password/change/` | 要 | パスワード変更 |
| GET | `/api/v1/auth/me/` | 要 | 自分の情報取得 |
| PATCH | `/api/v1/auth/me/` | 要 | プロフィール更新（表示名） |

### リクエスト / レスポンス例

```http
# 会員登録（トークンは返さない。登録後に別途ログインする）
POST /api/v1/auth/register/
{ "email": "alice@example.com", "password": "pass12345", "display_name": "アリス" }
-> 201  { "id": 1, "email": "alice@example.com", "display_name": "アリス" }

# ログイン
POST /api/v1/auth/token/
{ "email": "alice@example.com", "password": "pass12345" }
-> 200  { "access": "...", "refresh": "..." }

# 自分の情報
GET /api/v1/auth/me/        (Authorization: Bearer <access>)
-> 200  { "id": 1, "email": "alice@example.com", "display_name": "アリス" }

# プロフィール更新
PATCH /api/v1/auth/me/      (Authorization: Bearer <access>)
{ "display_name": "アリスちゃん" }
-> 200  { "id": 1, "email": "alice@example.com", "display_name": "アリスちゃん" }

# パスワード変更
POST /api/v1/auth/password/change/   (Authorization: Bearer <access>)
{ "current_password": "pass12345", "new_password": "newpass6789" }
-> 200  { "detail": "パスワードを変更しました。" }

# ログアウト
POST /api/v1/auth/logout/   (Authorization: Bearer <access>)
{ "refresh": "..." }
-> 205  (リフレッシュトークンを無効化)
```

## 6. ビジネスルール・バリデーション

- **email**：形式が正しいこと・**一意**であること。重複時は 400 `validation_error`。
- **password**：Django の標準バリデータを使用（最低8文字／よくあるPW不可／数字のみ不可／email・表示名と類似不可）。
- **display_name**：必須・最大50文字。
- **パスワード変更**：`current_password` が現在のパスワードと一致しない場合 400。新パスワードは上記ポリシー適用。
- **ログアウト**：渡された refresh トークンをブラックリスト登録し、以後 refresh 不可にする（`token_blacklist` アプリを有効化）。access トークンは寿命切れまで有効（短命で許容）。
- email は識別子のため**変更不可**（フェーズ1）。

### 6.1 エラー設計（エラー一覧）

レスポンスは統一フォーマット（[error-handling.md](../error-handling.md)）：`{"error": {"code", "message", "details?"}}`。

**方針**
- 入力値の検証エラー（serializer 由来）は一律 **400 `validation_error`** とし、`details` にフィールド別メッセージを入れる。
- 認証・トークン関連は simplejwt が返すコードを統一フォーマットに載せる（**401**）。
- サービス層の業務エラーは `core/exceptions.py` のドメイン例外を送出する。

| API | 失敗ケース | HTTP | `code` | 備考 |
|---|---|---|---|---|
| register | email 形式不正 / 必須欠落 | 400 | `validation_error` | `details.email` |
| register | email 重複 | 400 | `validation_error` | `details.email`（一意制約） |
| register | パスワードがポリシー違反 | 400 | `validation_error` | `details.password` |
| register | 表示名 未入力 / 50文字超過 | 400 | `validation_error` | `details.display_name` |
| token（ログイン） | 必須項目欠落 | 400 | `validation_error` | |
| token（ログイン） | 資格情報誤り / 無効化済みアカウント | 401 | `no_active_account` | simplejwt 既定 |
| token/refresh | refresh 欠落 | 400 | `validation_error` | |
| token/refresh | refresh が無効 / 期限切れ / ブラックリスト | 401 | `token_not_valid` | |
| token/verify | トークンが無効 | 401 | `token_not_valid` | |
| logout | 未認証 | 401 | `not_authenticated` | |
| logout | refresh 欠落 | 400 | `validation_error` | |
| logout | refresh が無効 / 既に無効化済み | 400 | `token_not_valid` | 冪等に扱う（再ログアウトでもエラーにしない方針も可） |
| password/change | 未認証 | 401 | `not_authenticated` | |
| password/change | current_password 不一致 | 400 | `validation_error` | `details.current_password` |
| password/change | new_password がポリシー違反 | 400 | `validation_error` | `details.new_password` |
| me（GET/PATCH） | 未認証 | 401 | `not_authenticated` | |
| me（PATCH） | display_name 50文字超過 | 400 | `validation_error` | `details.display_name` |
| me（PATCH） | email を変更しようとした | 200 | —（無視） | email は read-only。値は無視して更新成功 |
| 全認証必須API | トークン不正 / 期限切れ | 401 | `token_not_valid` / `authentication_failed` | |
| 全API | 不正な API バージョン（例 `/api/v2/`） | 404 | `not_found` | URLPathVersioning |

> パスワード・トークンの値そのものはレスポンス・ログに含めない。

## 7. 受け入れ基準（Acceptance Criteria）

- [ ] 有効な email/password/表示名で登録すると 201 が返り、ユーザーが作成される（トークンは返らない）。
- [ ] 登録後、その資格情報でログインしてトークンを取得できる。
- [ ] 既存 email で登録すると 400（`validation_error`）になる。
- [ ] 弱いパスワード（8文字未満等）は 400 で拒否される。
- [ ] 正しい資格情報でログインすると access/refresh が得られる。
- [ ] 誤った資格情報のログインは 401。
- [ ] access トークンで `/me` が取得でき、未認証では 401。
- [ ] `/me` の PATCH で表示名を更新できる。email は変更できない。
- [ ] パスワード変更後、新パスワードでログインでき、旧パスワードでは 401。
- [ ] ログアウトした refresh トークンでは token/refresh が 401 になる。
- [ ] エラー応答はすべて統一フォーマット `{"error": {"code", "message", ...}}` で、「6.1 エラー設計」表のステータス／コードに一致する。

## 8. テスト観点

- 正常系：登録→ログイン→/me→更新→パスワード変更→ログアウトの一連。
- 異常系：email 重複、弱いパスワード、誤資格情報、未認証アクセス、無効化済み refresh の利用。
- **エラー形式**：代表的な失敗ケースで `error.code` と HTTP ステータスが「6.1」表どおりか検証する。
- services（register / change_password など）の単体テストを優先。

## 9. 非機能・運用

- 権限：register/token 系は公開、それ以外は認証必須（既定の `IsAuthenticated`）。
- エラー形式は [error-handling.md](../error-handling.md) の統一フォーマット。

### 9.1 ログ設計（ログイベント一覧）

方針は [logging.md](../logging.md) に従う：**stdout 出力**、ロガーは `logging.getLogger(__name__)`（`accounts` 配下）、付加情報は `extra={...}` で構造化、**秘密情報・個人情報は出さない**。

**記録するイベント**

| イベント | レベル | logger | extra（記録する項目） |
|---|---|---|---|
| 会員登録 成功 | INFO | `accounts.services` | `user_id` |
| ログイン 成功 | INFO | `accounts`（token系） | `user_id` |
| ログイン 失敗（資格情報誤り） | WARNING | `accounts` | `email_masked`（例 `a***@example.com`） |
| ログアウト（無効化） 成功 | INFO | `accounts.services` | `user_id` |
| パスワード変更 成功 | INFO | `accounts.services` | `user_id` |
| プロフィール更新 成功 | INFO | `accounts.services` | `user_id`, `updated_fields`（例 `["display_name"]`） |
| 想定外エラー（500） | ERROR | 例外ハンドラ | `exc_info`（[error-handling.md](../error-handling.md) で集約） |

**ルール**

- **絶対に出さない**：パスワード（平文/ハッシュとも）、アクセス/リフレッシュトークンの値、email の生値。
- email を記録する必要がある場合（ログイン失敗の調査用）は**マスク**する（`email_masked`）。
- 入力バリデーションエラー（400）は通常イベントなので原則ログしない（必要時のみ DEBUG）。
- ログイン失敗を WARNING にするのは、連続失敗＝攻撃の兆候を検知できるようにするため。
- IP アドレスやレート制限の記録はフェーズ1では行わない（将来、不正検知を入れる際に検討）。

## 10. 未決事項 / TODO

- ~~登録時にトークンも返すか~~ → **返さない**で確定（メール確認導入時に矛盾しないため。登録 → ログインの2段）。
- フェーズ1では `is_active=True` で登録するが、メール確認（フェーズ2）導入時は `is_active=False` で登録し、確認後に有効化する想定。登録APIの契約（ユーザー情報のみ返す）は変えずに済む。
- リフレッシュトークンのローテーション（`ROTATE_REFRESH_TOKENS`）を有効にするか。
- 退会（アカウント削除）と、論理削除／物理削除の方針は別仕様で。
- パスワードリセット・メール確認はメール送信基盤の整備後（フェーズ2）。
