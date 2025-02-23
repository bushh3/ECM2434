from django.urls import path
from . import views

urlpatterns = [
    path('questions/', views.fetch_questions, name='fetch_questions'),  # 获取问题
    path('quiz-results/', views.quiz_results, name='quiz_results'),  # 获取分数
]