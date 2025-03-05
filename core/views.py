from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.db.models import F
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import json
import random
import os

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

def set_new_password(request):
    return render(request, 'core/set_new_password.html')


def home(request):
    if (request.user.is_authenticated):
        return render(request, 'core/navpage2.html')
    else:
        return HttpResponseRedirect('/login/')
        
def quiz(request):
    return render(request, 'core/quiz.html')
    
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

def profile_view(request):
    return render(request, 'core/profile.html')

@login_required
def upload_avatar(request): # 上传头像 Upload the avatar
    if request.method == "POST":
        if 'avatar' not in request.FILES:
            return JsonResponse({"success": False, "error": "No file uploaded"}, status=400, content_type="application/json")

        avatar_file = request.FILES['avatar']
        
        if not avatar_file.content_type.startswith('image/'):
            return JsonResponse({"success": False, "error": "Invalid file type"}, status=400, content_type="application/json")

        profile = get_object_or_404(Profile, user=request.user)

        if profile.avatar_url and profile.avatar_url != "avatars/fox.jpg":
            old_avatar_path = os.path.join(settings.MEDIA_ROOT, profile.avatar_url)
            if os.path.exists(old_avatar_path):
                os.remove(old_avatar_path)

        avatar_path = f'avatars/{avatar_file.name}'
        saved_path = default_storage.save(avatar_path, ContentFile(avatar_file.read()))
        profile.avatar_url = saved_path
        profile.save()

        return JsonResponse({"success": True, "avatarUrl": f"{settings.MEDIA_URL}{profile.avatar_url}"}, content_type="application/json")
    
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405, content_type="application/json")

@login_required
def get_user_profile(request): # Profile页面获取用户信息，包括打招呼的地方 Profile page obtain user information
    if request.method == "GET":
        user = request.user

        profile = get_object_or_404(Profile, user=user)
        avatar_url = f"{settings.MEDIA_URL}{profile.avatar_url}" if profile.avatar_url else f"{settings.MEDIA_URL}avatars/fox.jpg"
        return JsonResponse({
            "success": True,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "avatar_url": avatar_url
        })
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405, content_type="application/json")

@login_required
def get_avatar(request): # 获取用户头像 Obtain the user avatar
    if request.method == "GET":
        profile = get_object_or_404(Profile, user=request.user)
        if profile.avatar_url:
            avatar_url = f"{settings.MEDIA_URL}{profile.avatar_url}"
        else:
            avatar_url = f"{settings.MEDIA_URL}avatars/fox.jpg"
        return JsonResponse({"success": True, "avatar_url": avatar_url}, content_type="application/json")
    
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405, content_type="application/json")

@login_required
def delete_account(request): # 注销账号 Cancel the account
    if request.method == "DELETE":

        user = request.user
        user.delete()
        logout(request)
        return JsonResponse({"success": True, "message": "Account deleted successfully"}, content_type="application/json")

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405, content_type="application/json")

@login_required
def update_user_profile(request): # 修改个人信息Update the user information
    if request.method == "PUT":

        try:
            data = json.loads(request.body)
            user = request.user
            old_email = user.email
            new_email = data.get('email', user.email)

            if CustomUser.objects.filter(email=new_email).exclude(id=user.id).exists(): #检查邮箱名是否重复 Check whethe the email are duplicated
                return JsonResponse({"success": False, "error": "This email is already in use"}, status=400, content_type="application/json")

            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)

            user.save()

            email_changed = old_email != user.email
            if email_changed: #修改邮箱后要重新登录 User need to log in again after changing the email
                logout(request)
                return JsonResponse({"success": True, "message": "Profile updated successfully", "email_changed": True}, content_type="application/json")
            return JsonResponse({"success": True, "message": "Profile updated successfully"}, content_type="application/json")
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400, content_type="application/json")
    
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405, content_type="application/json")

@login_required
def change_password(request): # 已登录用户的重设密码 Reset the password of the logged-in user
    if request.method == "POST":

        try:
            data = json.loads(request.body)
            new_password = data.get("new_password")

            user = request.user

            validate_password(new_password, user)
            user.set_password(new_password)
            user.save()

            return JsonResponse({"success": True, "message": "Password updated successfully"}, content_type="application/json")
        except ValidationError as e:
            return JsonResponse({"success": False, "error": e.messages}, status=400, content_type="application/json")
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400, content_type="application/json")

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405, content_type="application/json")

@login_required
def logout_view(request): # 登出 Logout
    if request.method == "POST":

        logout(request)
        return JsonResponse({"success": True, "message": "Logged out successfully"}, content_type="application/json")
    
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405, content_type="application/json")  