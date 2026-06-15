"""accounts のルーティング。config/urls.py から /api/<version>/auth/ 配下で include。"""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("password/change/", views.PasswordChangeView.as_view(), name="password-change"),
    path("me/", views.MeView.as_view(), name="me"),
]
