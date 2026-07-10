"""User モデルの不変条件（DB 制約）のテスト。

Django は save() 時にモデル検証を行わないため、必須・一意といった不変条件は
DB の制約で守る。ここではその制約が実際に効いていることを確認する。
"""

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction

from tests.common import TEST_DISPLAY_NAME, TEST_EMAIL, TEST_PASSWORD, create_superuser, create_user

User = get_user_model()


@pytest.mark.django_db
def test_create_user_requires_email():
    """email が空なら ValueError（マネージャの明示的なガード）。"""
    with pytest.raises(ValueError):
        User.objects.create_user(email="", password=TEST_PASSWORD, display_name=TEST_DISPLAY_NAME)


@pytest.mark.django_db
def test_create_user_rejects_empty_display_name():
    """display_name を渡し忘れても空文字では保存できない（DB の CHECK 制約）。"""
    with pytest.raises(IntegrityError), transaction.atomic():
        User.objects.create_user(email=TEST_EMAIL, password=TEST_PASSWORD)


@pytest.mark.django_db
def test_create_user_accepts_valid_input():
    user = create_user()
    assert user.pk is not None
    assert user.email == TEST_EMAIL
    assert user.display_name == TEST_DISPLAY_NAME
    assert user.is_staff is False
    assert user.is_superuser is False


@pytest.mark.django_db
def test_create_superuser_sets_privilege_flags():
    admin = create_superuser()
    assert admin.is_staff is True
    assert admin.is_superuser is True
