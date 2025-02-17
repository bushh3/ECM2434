from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = "core"
urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name="core/login.html", next_page="../home",), name="login"),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name="password_reset"),
    path('signup/', views.signup, name="signup"),
]