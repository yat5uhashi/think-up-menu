"""アプリ全体で使うドメイン例外。

services / selectors はここで定義した例外を投げる。
HTTP ステータスへの変換は ``core.exception_handlers`` が行う（View 側で個別に
try/except する必要はない）。

詳細は docs/error-handling.md を参照。
"""


class ApplicationError(Exception):
    """業務ロジックのエラー基底。

    services / selectors から投げると、DRF の例外ハンドラが統一フォーマットの
    JSON レスポンスに変換する。

    Args:
        message: 利用者向けメッセージ。
        code: 機械可読なエラーコード（例: ``"recipe_not_found"``）。
        details: 補足情報（フィールド別エラーなど）。
    """

    default_message = "エラーが発生しました。"
    default_code = "error"
    status_code = 400

    def __init__(
        self,
        message: str | None = None,
        *,
        code: str | None = None,
        details: dict | None = None,
    ) -> None:
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(ApplicationError):
    """入力値が不正。"""

    default_message = "入力内容が正しくありません。"
    default_code = "validation_error"
    status_code = 400


class NotFoundError(ApplicationError):
    """対象が存在しない。"""

    default_message = "対象が見つかりません。"
    default_code = "not_found"
    status_code = 404


class PermissionDeniedError(ApplicationError):
    """権限がない。"""

    default_message = "この操作を行う権限がありません。"
    default_code = "permission_denied"
    status_code = 403


class ConflictError(ApplicationError):
    """状態の競合（重複登録など）。"""

    default_message = "処理が競合しました。"
    default_code = "conflict"
    status_code = 409
