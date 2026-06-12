"""JWT 認証と URL バージョニングのスモークテスト。

`uv run pytest` で実行される。詳細は docs/testing.md を参照。
"""

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient


@pytest.fixture
def client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
def test_jwt_token_obtain_success(client):
    """正しい資格情報で access / refresh トークンが取得できる。"""
    User.objects.create_user(username="alice", password="pass12345")

    res = client.post(
        "/api/v1/auth/token/",
        {"username": "alice", "password": "pass12345"},
        format="json",
    )

    assert res.status_code == 200
    assert "access" in res.data
    assert "refresh" in res.data


@pytest.mark.django_db
def test_jwt_token_obtain_invalid_credentials(client):
    """誤った資格情報では 401 が返る。"""
    res = client.post(
        "/api/v1/auth/token/",
        {"username": "nobody", "password": "wrong"},
        format="json",
    )

    assert res.status_code == 401


@pytest.mark.django_db
def test_unknown_api_version_is_rejected(client):
    """ALLOWED_VERSIONS 外のバージョンは受け付けない。"""
    res = client.post(
        "/api/v2/auth/token/",
        {"username": "x", "password": "y"},
        format="json",
    )

    # URLPathVersioning が不正バージョンを弾く（404）
    assert res.status_code == 404
