from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db.models import F
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
import json

def signup(request):
    # if no POST, display sign up page
    if request.POST == {}:
        return render(request, 'core/signup.html')
    
    # if POST
    else:
        # get information
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']

        # perhaps implement minimum length of password later??

        try:
            # create user
            user = User.objects.create_user(
            username=username, 
            email=email, 
            first_name=first_name, 
            last_name=last_name, 
            password=password
            )
            user.save()

            # add user as player in database
            player = Player(user=user)
            player.save()

            # authenticate and log in
            authenticated_user = authenticate(
            username=username, 
            password=password
            )
            
            if authenticated_user:
                login(request, authenticated_user)

            # redirect to home page
            # this may need changing, will be able to test once there is a home page
            return HttpResponseRedirect('/home/')
        
        # catch if username not unique
        except IntegrityError as e:
            error_message = "Username taken. Please enter a different username"
            
            # display signup page with error message
            return render(request, 'core/signup.html',
                          {"error_message": error_message})

def home(request):
    if (request.user.is_authenticated):
        return render(request, 'core/navpage2.html')
    else:
        return HttpResponseRedirect('/login/')
        
def quiz(request):
    return render(request, 'core/quiz.html')
    
# View to fetch all questions from the database
def fetch_questions(request):
    questions = Question.objects.all() 
    questions_json = json.dumps([
        {
            "id": question.id,
            "question_text": question.question_text,
            "options": [question.option1, question.option2, question.option3, question.option4],
            "correct_option": question.correct_option
        }
        for question in questions
    ])
    return render(request, 'core/questions.html', {'questions_json': questions_json})

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

    return render(request, 'core/result.html', {'result_text': result_text})  