"""ユーザー認証の受け入れ基準・エラー形式のテスト。

仕様: docs/specs/user-auth.md
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

REGISTER_URL = "/api/v1/auth/register/"
TOKEN_URL = "/api/v1/auth/token/"
REFRESH_URL = "/api/v1/auth/token/refresh/"
LOGOUT_URL = "/api/v1/auth/logout/"
PASSWORD_CHANGE_URL = "/api/v1/auth/password/change/"
ME_URL = "/api/v1/auth/me/"


@pytest.fixture
def client() -> APIClient:
    return APIClient()


def _create_user(email="alice@example.com", password="pass12345", display_name="アリス"):
    return User.objects.create_user(email=email, password=password, display_name=display_name)


def _login(client, email="alice@example.com", password="pass12345"):
    res = client.post(TOKEN_URL, {"email": email, "password": password}, format="json")
    return res


def _auth(client, user):
    client.force_authenticate(user=user)
    return client


# --- 会員登録 -------------------------------------------------------------


@pytest.mark.django_db
def test_register_success_returns_user_without_tokens(client):
    res = client.post(
        REGISTER_URL,
        {"email": "bob@example.com", "password": "pass12345", "display_name": "ボブ"},
        format="json",
    )
    assert res.status_code == 201
    assert res.data == {"id": res.data["id"], "email": "bob@example.com", "display_name": "ボブ"}
    assert "access" not in res.data and "refresh" not in res.data
    assert User.objects.filter(email="bob@example.com").exists()


@pytest.mark.django_db
def test_register_then_login(client):
    client.post(
        REGISTER_URL,
        {"email": "bob@example.com", "password": "pass12345", "display_name": "ボブ"},
        format="json",
    )
    res = _login(client, "bob@example.com", "pass12345")
    assert res.status_code == 200
    assert "access" in res.data and "refresh" in res.data


@pytest.mark.django_db
def test_register_duplicate_email_is_validation_error(client):
    _create_user(email="dup@example.com")
    res = client.post(
        REGISTER_URL,
        {"email": "dup@example.com", "password": "pass12345", "display_name": "x"},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "validation_error"
    assert "email" in res.data["error"]["details"]


@pytest.mark.django_db
def test_register_weak_password_is_rejected(client):
    res = client.post(
        REGISTER_URL,
        {"email": "weak@example.com", "password": "123", "display_name": "x"},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "validation_error"
    assert "password" in res.data["error"]["details"]


# --- ログイン -------------------------------------------------------------


@pytest.mark.django_db
def test_login_success(client):
    _create_user()
    res = _login(client)
    assert res.status_code == 200
    assert "access" in res.data and "refresh" in res.data


@pytest.mark.django_db
def test_login_invalid_credentials(client):
    _create_user()
    res = _login(client, password="wrongpass")
    assert res.status_code == 401
    assert res.data["error"]["code"] == "no_active_account"


# --- /me ------------------------------------------------------------------


@pytest.mark.django_db
def test_me_requires_authentication(client):
    res = client.get(ME_URL)
    assert res.status_code == 401
    assert res.data["error"]["code"] == "not_authenticated"


@pytest.mark.django_db
def test_me_get_and_update(client):
    user = _create_user()
    _auth(client, user)

    res = client.get(ME_URL)
    assert res.status_code == 200
    assert res.data["email"] == "alice@example.com"

    res = client.patch(ME_URL, {"display_name": "アリスちゃん"}, format="json")
    assert res.status_code == 200
    assert res.data["display_name"] == "アリスちゃん"


@pytest.mark.django_db
def test_me_email_is_read_only(client):
    user = _create_user()
    _auth(client, user)
    res = client.patch(ME_URL, {"email": "hacker@example.com"}, format="json")
    assert res.status_code == 200
    assert res.data["email"] == "alice@example.com"  # 変更されない


# --- パスワード変更 -------------------------------------------------------


@pytest.mark.django_db
def test_password_change_success(client):
    user = _create_user()
    _auth(client, user)
    res = client.post(
        PASSWORD_CHANGE_URL,
        {"current_password": "pass12345", "new_password": "newpass6789"},
        format="json",
    )
    assert res.status_code == 200

    fresh = APIClient()
    assert _login(fresh, password="pass12345").status_code == 401  # 旧PWは不可
    assert _login(fresh, password="newpass6789").status_code == 200  # 新PWで可


@pytest.mark.django_db
def test_password_change_wrong_current(client):
    user = _create_user()
    _auth(client, user)
    res = client.post(
        PASSWORD_CHANGE_URL,
        {"current_password": "wrong", "new_password": "newpass6789"},
        format="json",
    )
    assert res.status_code == 400
    assert res.data["error"]["code"] == "validation_error"
    assert "current_password" in res.data["error"]["details"]


# --- ログアウト -----------------------------------------------------------


@pytest.mark.django_db
def test_logout_blacklists_refresh_token(client):
    _create_user()
    tokens = _login(client).data
    auth = APIClient()
    auth.credentials(HTTP_AUTHORIZATION=f"Bearer {tokens['access']}")

    res = auth.post(LOGOUT_URL, {"refresh": tokens["refresh"]}, format="json")
    assert res.status_code == 205

    # 無効化された refresh では再発行できない
    res = client.post(REFRESH_URL, {"refresh": tokens["refresh"]}, format="json")
    assert res.status_code == 401
    assert res.data["error"]["code"] == "token_not_valid"


# --- バージョニング -------------------------------------------------------


@pytest.mark.django_db
def test_unknown_api_version_is_rejected(client):
    res = client.post(
        "/api/v2/auth/token/",
        {"email": "x@example.com", "password": "y"},
        format="json",
    )
    assert res.status_code == 404
    assert res.data["error"]["code"] == "not_found"
