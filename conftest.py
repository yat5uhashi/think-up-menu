"""pytest の共通 fixture。

このファイルはプロジェクト直下に置くため、pytest が自動で読み込み、
すべてのテストから import なしで fixture を利用できる。
テストデータ生成のヘルパーは tests/common.py にある。
"""

import pytest
from rest_framework.test import APIClient

from tests.common import create_user


@pytest.fixture
def api_client() -> APIClient:
    """未認証の API クライアント。"""
    return APIClient()


@pytest.fixture
def user(db):
    """テスト用の一般ユーザー（既定値）。"""
    return create_user()


@pytest.fixture
def auth_client(api_client: APIClient, user) -> APIClient:
    """``user`` で認証済みの API クライアント。"""
    api_client.force_authenticate(user=user)
    return api_client
