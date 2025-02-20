from django.urls import path
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
]