from django.contrib import admin  # 导入 admin 模块
from django.urls import path, include  # 导入 include 来包含 quiz 应用的 URL
from django.shortcuts import redirect
from django.views.generic.base import RedirectView
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from .forms import EmailBasedPasswordResetForm
from .views import CustomPasswordResetView, CustomPasswordResetConfirmView
from .views import get_user_info, scan_qr_code
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from . import views

app_name = "core"
urlpatterns = [
    path('', views.home, name="home"),
    path('login/', views.login_view, name="login"),
    path('password_reset/', CustomPasswordResetView.as_view(), name="password_reset"),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('signup/', views.signup, name="signup"),
    path('api/user/get-score/', views.get_user_score, name="get_user_score"),
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
    path('accounts/password_change/', PasswordChangeView.as_view(template_name='registration/password_change_form.html', success_url='/accounts/password_change/done/'), name='password_change'),
    path('accounts/password_change/done/', PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html'), name='password_change_done'),
    path('api/logout', views.logout_view, name="logout"),
    path('walkinggame/', views.walking_game, name="walkinggame"),
    path('walkinggame/save/', views.save_trip, name="save_trip"),
    path('walkinggame/history/', views.get_trip_history, name="get_trip_history"),
    path('recycling/', views.recycling_view, name='recycling'),
    path('recycling/user/info/', views.get_user_info, name='get_user_info'),
    path('recycling/scan/', views.scan_qr_code, name='scan_qr_code'),
    path('leaderboard/', views.leaderboard_view, name="leaderboard"),
    path('leaderboard/api/user_rank/', views.get_user_rank, name="user_rank"),
    path('leaderboard/api/rankings/', views.get_leaderboard, name='leaderboard_api'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)