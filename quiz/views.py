from django.http import HttpResponse
from .models import Question

# View to fetch all questions from the database
def fetch_questions(request):
    questions = Question.objects.all() 
    questions_data = ""

    # Loop through all questions and format the data as plain text
    for question in questions:
        question_data = f"{question.question_text}|{question.option1}|{question.option2}|{question.option3}|{question.option4}|{question.correct_option}\n"
        questions_data += question_data
    
    return HttpResponse(questions_data, content_type="text/plain")  

# View to check the user's answer for a specific question
def check_answer(request):
    if request.method == "POST":
        selected_option = request.POST.get('option')
        question_id = int(request.POST.get('question_id')) 
        
        try:
            #fetch the question by ID
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            # If the question does not exist, return an error
            return HttpResponse('Invalid question ID', status=400)

        # Check if the selected answer is correct
        if selected_option == question.correct_option:
            return HttpResponse('correct') 
        else:
            return HttpResponse(f'wrong-{question.correct_option}')
    
    return HttpResponse('Invalid request', status=400)

# View to get the quiz results
def get_quiz_results(request):
    correct = 5  
    wrong = 2  
    round_score = 75  
    total_score = 150  

    result_text = f"{correct}|{wrong}|{round_score}|{total_score}"

    return HttpResponse(result_text, content_type="text/plain")  
