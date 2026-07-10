"""テスト全体で共有するヘルパー（テストデータ生成など）。

どのアプリのテストからも次のように使える::

    from tests.common import create_user

    user = create_user()                          # 既定値のテストユーザー
    other = create_user(email="other@example.com")  # 一部だけ上書き

pytest の共通 fixture（api_client / user / auth_client）は
プロジェクト直下の conftest.py にある。
"""

from django.contrib.auth import get_user_model

# --- テスト用の既定値 ---------------------------------------------------
# 本番データと取り違えないよう、明らかにテストと分かる値にする。
# パスワードは Django の標準バリデータ（8文字以上・数字のみ不可・よくあるPW不可・
# email/表示名と類似不可）を通る値にしておく（登録APIのテストで使うため）。
TEST_EMAIL = "test-user@example.com"
TEST_PASSWORD = "test-password-123"
TEST_DISPLAY_NAME = "テストユーザー"

TEST_ADMIN_EMAIL = "test-admin@example.com"
TEST_ADMIN_DISPLAY_NAME = "テスト管理者"


def create_user(
    *,
    email: str = TEST_EMAIL,
    password: str = TEST_PASSWORD,
    display_name: str = TEST_DISPLAY_NAME,
    **extra_fields,
):
    """テスト用の一般ユーザーを作成して返す。

    Args:
        email: メールアドレス。省略時は ``TEST_EMAIL``。
        password: パスワード。省略時は ``TEST_PASSWORD``。
        display_name: 表示名。省略時は ``TEST_DISPLAY_NAME``。
        **extra_fields: その他のフィールド（``is_active`` など）。

    Returns:
        作成された User インスタンス。
    """
    # get_user_model() は import 時ではなく呼び出し時に評価する（アプリ未ロード対策）
    return get_user_model().objects.create_user(
        email=email, password=password, display_name=display_name, **extra_fields
    )


def create_superuser(
    *,
    email: str = TEST_ADMIN_EMAIL,
    password: str = TEST_PASSWORD,
    display_name: str = TEST_ADMIN_DISPLAY_NAME,
    **extra_fields,
):
    """テスト用の管理者ユーザー（is_staff/is_superuser）を作成して返す。"""
    return get_user_model().objects.create_superuser(
        email=email, password=password, display_name=display_name, **extra_fields
    )
