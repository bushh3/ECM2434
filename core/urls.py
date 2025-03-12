from django.contrib import admin  # 导入 admin 模块
from django.urls import path, include  # 导入 include 来包含 quiz 应用的 URL
from django.shortcuts import redirect
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from . import views

app_name = "core"
urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login_view, name="login"),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name="password_reset"),
    path('signup/', views.signup, name="signup"),
    path('quiz/', views.quiz, name="quiz"),
    path('questions/', views.fetch_questions, name="fetch_questions"),  # get question
    path('check-answer/', views.check_answer, name="check_answer"),  # check answer
    path('quiz-results/', views.get_quiz_results, name="get_quiz_results"),
    path('profile/', views.profile_view, name="profile"),
    path('leaderboard/', views.leaderboard_view, name="leaderboard"),
    path('admin/', admin.site.urls),
]

