from django.urls import path
from . import views

urlpatterns = [
    path('api/questions/', views.fetch_questions, name="fetch_questions"),  # get question
    path('api/check-answer/', views.check_answer, name="check_answer"),  # check answer
    path('api/quiz-results/', views.get_quiz_results, name="get_quiz_results"),  # get result
]