from django.contrib import admin  # 导入 admin 模块
from django.urls import path, include  # 导入 include 来包含 quiz 应用的 URL
from django.shortcuts import redirect
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from . import views

app_name = "core"
urlpatterns = [
    path('', views.home, name="home"),
    path('login/', auth_views.LoginView.as_view(template_name="core/login.html"), name="login"),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name="password_reset"),
    path('signup/', views.signup, name="signup"),
    path('admin/', admin.site.urls),  # 确保你已经导入了 admin 模块
    path('quiz/', include('quiz.urls')),  # 包含 quiz 应用的 URL 路由
]

