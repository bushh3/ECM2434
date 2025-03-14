from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.db.models import F
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
import json
import random

def login_view(request):
    form = AuthenticationForm(request, data=request.POST)
    if request.method != "POST":
        return render(request, "core/login.html")
    else:
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse("core:home"))
        else:
            return render(request,
                         "core/login.html",
                         {"form": form})

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
    
        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'core/signup.html', {"error_message": "Email already in use"})

        try:
            # create user
            user = CustomUser.objects.create_user(
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
            return HttpResponseRedirect('/home/')
        
        except IntegrityError:
            return render(request, 'core/signup.html', {"error_message": "An error occurred, please try again"})
        

def home(request):
    if (request.user.is_authenticated):
        return render(request, 'core/navpage2.html')
    else:
        return HttpResponseRedirect('/login/')
        
def quiz(request):
    return render(request, 'core/quiz.html')

def profile_view(request):
    return render(request, 'core/profile.html')
    
# View to fetch all questions from the database
def fetch_questions(request):
    questions = list(Question.objects.all()) 
    selected_questions = random.sample(questions, min(5, len(questions)))

    session_data = {
        str(index + 1): {
            'id': question.id,
            'correct_option': question.correct_option
        }
        for index, question in enumerate(selected_questions)
    }

    request.session['current_questions'] = session_data
    request.session.modified = True  # make sure that the session changes take effect

    questions_json = json.dumps([
        {
            "id": question.id,
            "question_text": question.question_text,
            "options": [question.option1, question.option2, question.option3, question.option4],
            "correct_option": question.correct_option
        }
        for question in selected_questions
    ])
    return render(request, 'core/questions.html', {'questions_json': questions_json})

# View to check the user's answer for a specific question
@login_required
def check_answer(request):
    if request.method == "POST":
        session_questions = request.session.get('current_questions', {})
        total_questions = len(session_questions)
        score_per_question = 5
        
        correct = 0
        wrong = 0

        for key, user_answer in request.POST.items():
            if key.startswith('question_'):
                question_index = key.split('_')[1]
                
                # get the correct option
                correct_option = session_questions.get(question_index, {}).get('correct_option')
                if correct_option and user_answer == correct_option:
                    correct += 1
                else:
                    wrong += 1
        
        # calculate the score
        current_score = correct * score_per_question
        
        player = request.user.player
        player.points += current_score
        player.save()

        # log to session
        request.session['quiz_result'] = {
            'correct': correct,
            'wrong': wrong,
            'current_score': current_score,
            'total_score': player.points
        }
        # request.session['total_score'] = total_score
        request.session.modified = True

        return HttpResponseRedirect(reverse('core:get_quiz_results'))

@login_required
def get_quiz_results(request):
    player = request.user.player
    quiz_result = request.session.get('quiz_result', {
        'correct': 0,
        'wrong': 0,
        'current_score': 0,
        'total_score': player.points
    })

    correct = quiz_result['correct']
    wrong = quiz_result['wrong']
    current_score = quiz_result['current_score']
    total_score = quiz_result['total_score']
    
    result_text = f"{correct}|{wrong}|{current_score}|{total_score}"
    
    return render(request, 'core/result.html', {'result_text': result_text})  