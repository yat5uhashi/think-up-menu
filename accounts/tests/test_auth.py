"""ユーザー認証の受け入れ基準・エラー形式のテスト。

仕様: docs/specs/user-auth.md
共通ヘルパーは tests/common.py、共通 fixture は conftest.py を参照。
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tests.common import TEST_DISPLAY_NAME, TEST_EMAIL, TEST_PASSWORD

REGISTER_URL = "/api/v1/auth/register/"
TOKEN_URL = "/api/v1/auth/token/"
REFRESH_URL = "/api/v1/auth/token/refresh/"
LOGOUT_URL = "/api/v1/auth/logout/"
PASSWORD_CHANGE_URL = "/api/v1/auth/password/change/"
ME_URL = "/api/v1/auth/me/"

NEW_PASSWORD = "new-password-456"


def _login(client, email=TEST_EMAIL, password=TEST_PASSWORD):
    """ログインAPIを呼びレスポンスを返す。"""
    return client.post(TOKEN_URL, {"email": email, "password": password}, format="json")


# --- 会員登録 -------------------------------------------------------------


@pytest.mark.django_db
def test_register_success_returns_user_without_tokens(api_client):
    res = api_client.post(
        REGISTER_URL,
        {"email": "new-user@example.com", "password": TEST_PASSWORD, "display_name": "ボブ"},
        format="json",
    )
    assert res.status_code == 201
    assert res.data["email"] == "new-user@example.com"
    assert res.data["display_name"] == "ボブ"
    assert set(res.data) == {"id", "email", "display_name"}  # トークンは含まれない
    assert get_user_model().objects.filter(email="new-user@example.com").exists()


@pytest.mark.django_db
def test_register_then_login(api_client):
    api_client.post(
        REGISTER_URL,
        {"email": "new-user@example.com", "password": TEST_PASSWORD, "display_name": "ボブ"},
        format="json",
    )
    res = _login(api_client, "new-user@example.com", TEST_PASSWORD)
    assert res.status_code == 200
    assert "access" in res.data and "refresh" in res.data


@pytest.mark.django_db
def test_register_duplicate_email_is_validation_error(api_client, user):
    res = api_client.post(
        REGISTER_URL,
        {"email": TEST_EMAIL, "password": TEST_PASSWORD, "display_name": "x"},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "validation_error"
    assert "email" in res.data["error"]["details"]


@pytest.mark.django_db
def test_register_weak_password_is_rejected(api_client):
    res = api_client.post(
        REGISTER_URL,
        {"email": "weak@example.com", "password": "123", "display_name": "x"},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "validation_error"
    assert "password" in res.data["error"]["details"]


@pytest.mark.django_db
def test_register_invalid_email_format_is_rejected(api_client):
    res = api_client.post(
        REGISTER_URL,
        {"email": "not-an-email", "password": TEST_PASSWORD, "display_name": "x"},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "validation_error"
    assert "email" in res.data["error"]["details"]


@pytest.mark.django_db
def test_register_too_long_display_name_is_rejected(api_client):
    """max_length=50 はシリアライザが弾き、DB まで到達させない。"""
    res = api_client.post(
        REGISTER_URL,
        {"email": "long@example.com", "password": TEST_PASSWORD, "display_name": "X" * 51},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "validation_error"
    assert "display_name" in res.data["error"]["details"]


# --- email の正規化（大文字小文字を同一視） -------------------------------


@pytest.mark.django_db
def test_register_normalizes_email_to_lowercase(api_client):
    """大文字混じりで登録しても小文字に正規化して保存される。"""
    res = api_client.post(
        REGISTER_URL,
        {
            "email": "Alice@Example.COM",
            "password": TEST_PASSWORD,
            "display_name": TEST_DISPLAY_NAME,
        },
        format="json",
    )
    assert res.status_code == 201
    assert res.data["email"] == "alice@example.com"
    assert get_user_model().objects.filter(email="alice@example.com").exists()


@pytest.mark.django_db
def test_register_duplicate_email_differing_case_is_rejected(api_client, user):
    """大文字違いの同一アドレスは重複として弾く。"""
    res = api_client.post(
        REGISTER_URL,
        {"email": TEST_EMAIL.upper(), "password": TEST_PASSWORD, "display_name": "x"},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "validation_error"
    assert "email" in res.data["error"]["details"]


@pytest.mark.django_db
def test_login_is_case_insensitive(api_client, user):
    """小文字で登録したアドレスに大文字混じりでもログインできる。"""
    res = _login(api_client, email=TEST_EMAIL.upper())
    assert res.status_code == 200
    assert "access" in res.data


# --- ログイン -------------------------------------------------------------


@pytest.mark.django_db
def test_login_success(api_client, user):
    res = _login(api_client)
    assert res.status_code == 200
    assert "access" in res.data and "refresh" in res.data


@pytest.mark.django_db
def test_login_invalid_credentials(api_client, user):
    res = _login(api_client, password="wrong-password")
    assert res.status_code == 401
    assert res.data["error"]["code"] == "no_active_account"


# --- /me ------------------------------------------------------------------


@pytest.mark.django_db
def test_me_requires_authentication(api_client):
    res = api_client.get(ME_URL)
    assert res.status_code == 401
    assert res.data["error"]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_me_get_and_update(auth_client):
    res = auth_client.get(ME_URL)
    assert res.status_code == 200
    assert res.data["email"] == TEST_EMAIL

    res = auth_client.patch(ME_URL, {"display_name": "更新後の名前"}, format="json")
    assert res.status_code == 200
    assert res.data["display_name"] == "更新後の名前"


@pytest.mark.django_db
def test_me_email_is_read_only(auth_client):
    res = auth_client.patch(ME_URL, {"email": "hacker@example.com"}, format="json")
    assert res.status_code == 200
    assert res.data["email"] == TEST_EMAIL  # 変更されない


# --- パスワード変更 -------------------------------------------------------


@pytest.mark.django_db
def test_password_change_success(auth_client):
    res = auth_client.post(
        PASSWORD_CHANGE_URL,
        {"current_password": TEST_PASSWORD, "new_password": NEW_PASSWORD},
        format="json",
    )
    assert res.status_code == 200

    fresh = APIClient()
    assert _login(fresh, password=TEST_PASSWORD).status_code == 401  # 旧PWは不可
    assert _login(fresh, password=NEW_PASSWORD).status_code == 200  # 新PWで可


@pytest.mark.django_db
def test_password_change_wrong_current(auth_client):
    res = auth_client.post(
        PASSWORD_CHANGE_URL,
        {"current_password": "wrong-password", "new_password": NEW_PASSWORD},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "validation_error"
    assert "current_password" in res.data["error"]["details"]


# --- ログアウト -----------------------------------------------------------


@pytest.mark.django_db
def test_logout_blacklists_refresh_token(api_client, user):
    tokens = _login(api_client).data
    authed = APIClient()
    authed.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    res = authed.post(LOGOUT_URL, {"refresh": tokens["refresh"]}, format="json")
    assert res.status_code == 205

    # 無効化された refresh では再発行できない
    res = api_client.post(REFRESH_URL, {"refresh": tokens["refresh"]}, format="json")
    assert res.status_code == 401
    assert res.data["error"]["code"] == "token_not_valid"


# --- バージョニング -------------------------------------------------------


@pytest.mark.django_db
def test_unknown_api_version_is_rejected(api_client):
    res = api_client.post(
        "/api/v2/auth/token/",
        {"email": "x@example.com", "password": "y"},
        format="json",
    )
    assert res.status_code == 404
    assert res.data["error"]["code"] == "not_found"
