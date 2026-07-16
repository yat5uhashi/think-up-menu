"""accounts の DRF ビュー（薄く保つ：検証→サービス呼び出し→レスポンス）。

詳細は docs/specs/user-auth.md を参照。
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from . import services
from .serializers import (
    LogoutSerializer,
    PasswordChangeSerializer,
    RegisterSerializer,
    UserSerializer,
)


class RegisterView(APIView):
    """会員登録。成功で 201（ユーザー情報のみ。トークンは返さない）。"""

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = services.register_user(**serializer.validated_data)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class MeView(APIView):
    """自分の情報の取得（GET）とプロフィール更新（PATCH）。"""

    def get(self, request, *args, **kwargs):
        return Response(UserSerializer(request.user).data)

    def patch(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        user = services.update_profile(
            user=request.user,
            display_name=serializer.validated_data.get("display_name", request.user.display_name),
        )
        return Response(UserSerializer(user).data)


class PasswordChangeView(APIView):
    """ログイン中ユーザーのパスワード変更。"""

    def post(self, request, *args, **kwargs):
        serializer = PasswordChangeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        services.change_password(
            user=request.user, new_password=serializer.validated_data["new_password"]
        )
        return Response({"detail": "パスワードを変更しました。"})


class LogoutView(APIView):
    """リフレッシュトークンを無効化する。"""

    def post(self, request, *args, **kwargs):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        services.logout(
            user_id=request.user.id,
            refresh_token=serializer.validated_data["refresh"],
        )
        return Response(status=status.HTTP_205_RESET_CONTENT)
