"""UserManager がモデルの不変条件を守ることのテスト。

Django は save() 時にモデル検証を行わないため、_create_user() が full_clean() で
必須・最大長・形式を強制していることを確認する（ORM 直呼び経路の防御）。
"""

import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from tests.common import TEST_DISPLAY_NAME, TEST_EMAIL, TEST_PASSWORD, create_user

User = get_user_model()


@pytest.mark.django_db
def test_create_user_requires_email():
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password=TEST_PASSWORD, display_name=TEST_DISPLAY_NAME)


@pytest.mark.django_db
def test_create_user_requires_display_name():
    """display_name を渡し忘れても空文字で保存されず、検証エラーになる。"""
    with pytest.raises(ValidationError) as exc:
        User.objects.create_user(email=TEST_EMAIL, password=TEST_PASSWORD)
    assert "display_name" in exc.value.message_dict


@pytest.mark.django_db
def test_create_user_rejects_too_long_display_name():
    """max_length=50 を超える表示名は DB に依存せず検証で弾く。"""
    with pytest.raises(ValidationError) as exc:
        create_user(display_name="X" * 51)
    assert "display_name" in exc.value.message_dict


@pytest.mark.django_db
def test_create_user_rejects_invalid_email_format():
    with pytest.raises(ValidationError) as exc:
        create_user(email="not-an-email")
    assert "email" in exc.value.message_dict


@pytest.mark.django_db
def test_create_user_accepts_valid_input():
    user = create_user()
    assert user.pk is not None
    assert user.display_name == TEST_DISPLAY_NAME
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_create_superuser_sets_privilege_flags():
    from tests.common import create_superuser

    admin = create_superuser()
    assert admin.is_staff is True
    assert admin.is_superuser is True
