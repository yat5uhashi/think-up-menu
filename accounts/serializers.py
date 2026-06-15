"""accounts の DRF シリアライザ（入力検証・出力変換）。

検証はここ。ビジネスロジック（永続化）は services.py に置く。
詳細は docs/specs/user-auth.md を参照。
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """自分の情報の表現。GET の出力と PATCH（表示名更新）に使う。"""

    class Meta:
        model = User
        fields = ["id", "email", "display_name"]
        read_only_fields = ["id", "email"]  # email は識別子のため変更不可


class RegisterSerializer(serializers.ModelSerializer):
    """会員登録の入力検証。"""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "password", "display_name"]

    def validate(self, attrs):
        # email/display_name と類似のパスワードも弾けるよう、仮ユーザーで検証する
        candidate = User(email=attrs.get("email", ""), display_name=attrs.get("display_name", ""))
        try:
            validate_password(attrs["password"], candidate)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)}) from exc
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """パスワード変更の入力検証（context に request が必要）。"""

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("現在のパスワードが正しくありません。")
        return value

    def validate_new_password(self, value):
        user = self.context["request"].user
        try:
            validate_password(value, user)
        except DjangoValidationError as exc:
            raise serializers.ValidationError(list(exc.messages)) from exc
        return value


class LogoutSerializer(serializers.Serializer):
    """ログアウト（リフレッシュトークンの無効化）の入力。"""

    refresh = serializers.CharField()
