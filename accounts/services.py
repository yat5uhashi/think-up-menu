"""accounts の書き込み系ビジネスロジック。

View からはここを呼ぶ（View は薄く保つ）。request は受け取らず、必要な値を引数で受ける。
詳細は docs/architecture.md / docs/specs/user-auth.md を参照。
"""

import logging

from django.contrib.auth import get_user_model
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from core.exceptions import ValidationError

User = get_user_model()
logger = logging.getLogger(__name__)


def register_user(*, email: str, password: str, display_name: str) -> "User":
    """ユーザーを1件作成して返す。"""
    user = User.objects.create_user(email=email, password=password, display_name=display_name)
    logger.info("user registered", extra={"user_id": user.id})
    return user


def change_password(*, user: "User", new_password: str) -> None:
    """ログイン中ユーザーのパスワードを変更する。"""
    user.set_password(new_password)
    user.save(update_fields=["password"])
    logger.info("password changed", extra={"user_id": user.id})


def update_profile(*, user: "User", display_name: str) -> "User":
    """プロフィール（表示名）を更新する。"""
    user.display_name = display_name
    user.save(update_fields=["display_name"])
    logger.info(
        "profile updated",
        extra={"user_id": user.id, "updated_fields": ["display_name"]},
    )
    return user


def logout(*, user_id: int, refresh_token: str) -> None:
    """リフレッシュトークンを無効化（ブラックリスト登録）する。"""
    try:
        RefreshToken(refresh_token).blacklist()
    except TokenError as exc:
        raise ValidationError("無効なトークンです。", code="token_not_valid") from exc
    logger.info("user logged out", extra={"user_id": user_id})
