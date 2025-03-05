from django.contrib import admin  # 导入 admin 模块
from django.urls import path, include  # 导入 include 来包含 quiz 应用的 URL
from django.shortcuts import redirect
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

app_name = "core"
urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login_view, name="login"),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name="password_reset"), #这是Django自带的需要邮件验证的
    path('set_new_password/', views.set_new_password, name="set_new_password"), #这需要我们自己创建的
    path('signup/', views.signup, name="signup"),
    path('quiz/', views.quiz, name="quiz"),
    path('questions/', views.fetch_questions, name="fetch_questions"),  # get question
    path('check-answer/', views.check_answer, name="check_answer"),  # check answer
    path('quiz-results/', views.get_quiz_results, name="get_quiz_results"),
    path('admin/', admin.site.urls),
    path('profile/', views.profile_view, name="profile"),
    path('api/user/avatar', views.upload_avatar, name="upload_avatar"),
    path('api/user/profile', views.get_user_profile, name="get_user_profile"),
    path('api/user/get-avatar', views.get_avatar, name="get_avatar"),
    path('api/user/delete', views.delete_account, name="delete_account"),
    path('api/user/update', views.update_user_profile, name="update_user_profile"),
    path('api/user/change-password', views.change_password, name="change_password"),
    path('api/logout', views.logout_view, name="logout"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

