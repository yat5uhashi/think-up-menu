"""テスト共通のヘルパー。

複数のテストで使い回す処理（ユーザー生成・認証）を置く。
他アプリのテストからも次のように使える::

    from accounts.tests.common import create_user

pytest の収集対象は ``test_*.py`` のみなので、このファイルはテストとして実行されない。
"""

from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

# テスト用の既定値（本番データと取り違えないよう、test と分かる値にする）
TEST_EMAIL = "test.user@example.com"
TEST_PASSWORD = "test-password-12345"
TEST_DISPLAY_NAME = "テストユーザー"

TEST_ADMIN_EMAIL = "test.admin@example.com"
TEST_ADMIN_DISPLAY_NAME = "テスト管理者"


def create_user(
    *,
    email: str = TEST_EMAIL,
    password: str = TEST_PASSWORD,
    display_name: str = TEST_DISPLAY_NAME,
    **extra_fields,
) -> "User":
    """テスト用の一般ユーザーを作成して返す。

    Args:
        email: メールアドレス。省略時は ``TEST_EMAIL``。
        password: 生パスワード。省略時は ``TEST_PASSWORD``。
        display_name: 表示名。省略時は ``TEST_DISPLAY_NAME``。
        **extra_fields: User モデルのその他フィールド。

    Returns:
        作成された一般ユーザー（is_staff=False, is_superuser=False）。
    """
    return User.objects.create_user(
        email=email, password=password, display_name=display_name, **extra_fields
    )


def create_superuser(
    *,
    email: str = TEST_ADMIN_EMAIL,
    password: str = TEST_PASSWORD,
    display_name: str = TEST_ADMIN_DISPLAY_NAME,
    **extra_fields,
) -> "User":
    """テスト用の管理者ユーザーを作成して返す。"""
    return User.objects.create_superuser(
        email=email, password=password, display_name=display_name, **extra_fields
    )


def authenticate(client: APIClient, user: "User") -> APIClient:
    """APIClient を指定ユーザーで認証済みにして返す。"""
    client.force_authenticate(user=user)
    return client
