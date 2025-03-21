from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy, get_resolver
from django.db.models import F
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import views as auth_views
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils import timezone
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
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
    if request.method == "POST":

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

            return render(request, 'core/signup.html', {"success": True})
        
        except IntegrityError:
            return render(request, 'core/signup.html', {"error_message": "An error occurred, please try again"})
        
    return render(request, 'core/signup.html')

def set_new_password(request):
    return render(request, 'core/set_new_password.html')
        
def home(request):
    if (request.user.is_authenticated):
        return render(request, 'core/navpage2.html')
    else:
        return HttpResponseRedirect('/login/')
        
@login_required
def get_user_score(request):
    user = request.user
    try:
        player = Player.objects.get(user=user)
        return JsonResponse({"success": True, "score": player.points})
    except Player.DoesNotExist:
        return JsonResponse({"success": False, "error": "Player profile not found"}, status=404)
        
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

@login_required
def walking_game(request):
    return render(request, 'core/walkinggame.html')

@login_required
def save_trip(request):
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        if not session_id:
            return JsonResponse({'error': 'session_id cannot be empty'}, status=400)
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        distance = request.POST.get('distance')
        duration = request.POST.get('duration')
        is_completed = request.POST.get('is_completed') == 'true'
        points_earned = 30 if is_completed else 0

        track_points = []
        track_points_count = int(request.POST.get('track_points_count', 0))

        # Collecting track points from the POST request
        for i in range(track_points_count):
                lat = request.POST.get(f'point_lat_{i}')
                lon = request.POST.get(f'point_lng_{i}')
                timestamp = request.POST.get(f'point_time_{i}')
                if lat and lon and timestamp:
                    track_points.append({"lat": lat, "lon": lon, "timestamp": timestamp})

        track_points_json = json.dumps(track_points)
        player = request.user.player
        # Create or update the walking challenge
        challenge, created = WalkingChallenge.objects.update_or_create(
            session_id=session_id,
            player=player,
            defaults={
                'start_time': start_time,
                'end_time': end_time,
                'distance': distance,
                'duration': duration,
                'is_completed': is_completed,
                'points_earned': points_earned,
                'track_points': track_points_json,
            }
        )

        player.points += points_earned
        player.save()

        return JsonResponse({'message': 'Trip data saved successfully.', 'status': 200})

    return JsonResponse({'error': 'Invalid request.', 'status': 400}, status=400)

@login_required
def get_trip_history(request):
    if not hasattr(request.user, 'player'):
        Player.objects.create(user=request.user, points=0)
    player = request.user.player
    trips = WalkingChallenge.objects.filter(player=player).order_by('-start_time')

    history_html = '<h2 class="history-title">Activity History</h2><div class="history-list">'

    if trips.exists():
        for trip in trips:
            status_class = "status-complete" if trip.is_completed else "status-incomplete"
            item_class = "history-item success" if trip.is_completed else "history-item incomplete"
            status_text = "Completed" if trip.is_completed else "Incomplete"
            points_text = f"{trip.points_earned} Points" if trip.is_completed else "No Points"

            try:
                duration_milliseconds = float(trip.duration)
             
                duration_seconds = duration_milliseconds / 1000
            
                minutes = int(duration_seconds // 60)
                seconds = int(duration_seconds % 60)
               
                duration_text = f"{minutes} min {seconds} sec"
            except (ValueError, TypeError):
                
                duration_text = "0 min 0 sec"
                print(f"Error processing duration: {trip.duration}, type: {type(trip.duration)}")

            history_html += f"""
                <div class="{item_class}">
                    <div class="history-meta">
                        <span class="history-time">{trip.start_time.strftime('%Y-%m-%d %H:%M:%S')}</span>
                        <span class="history-status {status_class}">{status_text}</span>
                    </div>
                    <div class="history-stats">
                        <div class="history-stat">
                            <span class="history-stat-value">{trip.distance:.1f} km</span>
                            <span class="history-stat-label">Distance</span>
                        </div>
                        <div class="history-stat">
                            <span class="history-stat-value">{duration_text}</span>
                            <span class="history-stat-label">Duration</span>
                        </div>
                        <div class="history-stat">
                            <span class="history-stat-value">{points_text}</span>
                            <span class="history-stat-label">Points</span>
                        </div>
                    </div>
                </div>
            """
    else:
        history_html += '<div class="no-records">No travel records yet. Start your green travel journey!</div>'

    history_html += '</div>'
    return HttpResponse(history_html, status=200)



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

        request.session.flush()
        response = JsonResponse({"success": True, "message": "Logged out successfully"}, content_type="application/json")
        response.delete_cookie("sessionid")
        response.delete_cookie("csrftoken")
        return response
    
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405, content_type="application/json") 
    
class CustomPasswordResetView(auth_views.PasswordResetView):
    def form_valid(self, form):
        users = list(form.get_users(form.cleaned_data["email"]))
        if not users:
            return super().form_invalid(form)

        user = users[0]
        uidb64 = urlsafe_base64_encode(force_bytes(user.id))
        token = default_token_generator.make_token(user)

        reset_url = self.request.build_absolute_uri(
            reverse('core:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        )

        form.save(
            request=self.request,
            use_https=self.request.is_secure(),
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            token_generator=default_token_generator,
            extra_email_context={'password_reset_confirm_url': reset_url},
        )
        return super().form_valid(form)
    
class CustomPasswordResetConfirmView(auth_views.PasswordResetConfirmView):
    success_url = reverse_lazy('core:password_reset_complete') 