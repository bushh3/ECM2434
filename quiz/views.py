from django.http import HttpResponse
from .models import Question

def fetch_questions(request):
    questions = Question.objects.all() 
    questions_data = []

    for question in questions:
        question_data = {
            'text': question.question_text,
            'options': {
                'A': question.option1,
                'B': question.option2,
                'C': question.option3,
                'D': question.option4,
            },
            'correctAnswer': question.correct_option, 
        }
        questions_data.append(question_data)

    return HttpResponse("Questions data: Placeholder for questions", content_type="text/plain")

def quiz_results(request):

    correct = 5
    wrong = 2
    round_score = 75
    total_score = 150

    result = f"{correct}|{wrong}|{round_score}|{total_score}"

    return HttpResponse(result, content_type="text/plain")
