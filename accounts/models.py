"""ユーザーモデル（email を識別子とするカスタムユーザー）。

username を廃止し、email でログインする。詳細は docs/specs/user-auth.md を参照。
"""

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    """email を識別子とするユーザーマネージャ。"""

    use_in_migrations = True

    @classmethod
    def normalize_email(cls, email: str) -> str:
        """メールアドレスを小文字に正規化する。

        Django 標準の ``normalize_email`` はドメイン部しか小文字化しないため、
        ローカル部も含めて全体を小文字にする。RFC 5321 上ローカル部は大文字小文字を
        区別しうるが、実運用のメールプロバイダは区別せず、区別すると同一受信箱に
        対して重複アカウントが作れてしまうため同一視する。
        """
        return super().normalize_email(email).lower()

    def get_by_natural_key(self, username: str):
        """メールアドレスの大文字小文字を区別せずにユーザーを取得する（ログインで使用）。"""
        return self.get(**{f"{self.model.USERNAME_FIELD}__iexact": username})

    def _create_user(self, email: str, password: str | None, **extra_fields):
        if not email:
            raise ValueError("email は必須です。")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("スーパーユーザーは is_staff=True である必要があります。")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("スーパーユーザーは is_superuser=True である必要があります。")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """email でログインするユーザー。

    AbstractUser から username を取り除き、email を一意な識別子にする。
    表示名(display_name)を持つ。
    """

    username = None
    email = models.EmailField("メールアドレス", unique=True)
    display_name = models.CharField("表示名", max_length=50)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["display_name"]  # createsuperuser で email/password 以外に要求

    objects = UserManager()

    def __str__(self) -> str:
        return self.email
