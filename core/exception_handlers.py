"""DRF 用のカスタム例外ハンドラ。

すべての API エラーを次の統一フォーマットで返す::

    {
      "error": {
        "code": "validation_error",
        "message": "入力内容が正しくありません。",
        "details": {...}        # 任意
      }
    }

settings.py の ``REST_FRAMEWORK["EXCEPTION_HANDLER"]`` に登録する。
詳細は docs/error-handling.md を参照。
"""

import logging

from rest_framework import exceptions as drf_exceptions
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler

from core.exceptions import ApplicationError

logger = logging.getLogger(__name__)


def _error_body(*, code: str, message: str, details: dict | None = None) -> dict:
    body = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return body


def custom_exception_handler(exc, context):
    """DRF が捕捉した例外を統一フォーマットの Response に変換する。"""
    # 1) 自作のドメイン例外
    if isinstance(exc, ApplicationError):
        if exc.status_code >= 500:
            logger.error("application error: %s", exc.message, exc_info=exc)
        else:
            logger.info("application error: %s (%s)", exc.message, exc.code)
        return Response(
            _error_body(code=exc.code, message=exc.message, details=exc.details),
            status=exc.status_code,
        )

    # 2) DRF 標準例外（ValidationError / NotFound / NotAuthenticated 等）
    response = drf_exception_handler(exc, context)
    if response is not None:
        code = getattr(exc, "default_code", "error")
        if isinstance(exc, drf_exceptions.ValidationError):
            # フィールド別エラーは details に格納する
            message = "入力内容が正しくありません。"
            details = (
                response.data if isinstance(response.data, dict) else {"errors": response.data}
            )
        else:
            detail = response.data.get("detail") if isinstance(response.data, dict) else None
            message = str(detail) if detail else "エラーが発生しました。"
            details = None
        response.data = _error_body(code=code, message=message, details=details)
        return response

    # 3) 想定外の例外（DRF が処理しない＝500 相当）はここで握りつぶさず、
    #    ログだけ残して None を返す（Django 既定の 500 ハンドリングに委ねる）。
    logger.exception("unhandled exception", exc_info=exc)
    return None
