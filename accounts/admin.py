"""管理画面でのユーザー登録（email ベースのカスタムユーザー用）。"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """email ベースのカスタムユーザー用の管理画面設定。"""

    ordering = ["email"]
    list_display = ["email", "display_name", "is_staff", "is_active"]
    search_fields = ["email", "display_name"]
    # username を持たないので fieldsets を email ベースに差し替える
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("個人情報", {"fields": ("display_name",)}),
        (
            "権限",
            {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")},
        ),
        ("日時", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "display_name", "password1", "password2"),
            },
        ),
    )
