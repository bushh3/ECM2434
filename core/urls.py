from django.contrib import admin
from django.urls import path, include
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
    path('walkinggame/', views.walking_game, name="walkinggame"),
    path('walkinggame/save/', views.save_trip, name="save_trip"),  # Save trip data
    path('walkinggame/history/', views.get_trip_history, name="get_trip_history"),  # Get trip history
    path('walkinggame/delete/', views.delete_trip, name="delete_trip"),  # Delete trip record
    
    path('admin/', admin.site.urls),
]

