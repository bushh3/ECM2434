"""
Author: Zhiqiao Luo, Wayuan Xiao

Main functionalities:

- User Authentication and Management: 
User login (login_view)
User registration (signup)
Set new password page (set_new_password)
User logout (logout_view)
Update user profile (update_user_profile)
Change user password (change_password)
Delete user account (delete_account)

- Scoring and Ranking:
Get user score (get_user_score)
Get user rank (get_user_rank)
Save trip data for walking challenge (save_trip)
Get trip history (get_trip_history)
Scan QR code to earn points (scan_qr_code)
Get leaderboard (get_leaderboard)

- Game Functionality:
Quiz game page (quiz)
Check answers and update score (check_answer)
Display quiz results (get_quiz_results)
Walking game page (walking_game)

- User Profile and Avatar:
User profile page (profile_view)
Upload user avatar (upload_avatar)
Get user profile data (get_user_profile)
Get user avatar (get_avatar)

- Password Reset Functionality:
Custom password reset view (CustomPasswordResetView)
Password reset confirmation (CustomPasswordResetConfirmView)

- Recycling Functionality:
Recycling bin page (recycling_view)

- Additional Features:
Fetch quiz questions (fetch_questions)
Get user information (points and last scan date) (get_user_info)
"""

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
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
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
from django.templatetags.static import static
import json
import random
import os


"""
Handles user login using email and password, redirecting to the homepage on success.
"""
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
        

"""
manages user registration, creates a new account and logs the user in
"""
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


"""
renders the page for users to set a new password
"""        
def set_new_password(request):
    return render(request, 'core/set_new_password.html')
    
def home(request):
    if (request.user.is_authenticated):
        return render(request, 'core/navpage2.html')
    else:
        return HttpResponseRedirect('/login/')
        
@login_required
def get_user_score(request):
    """
    Gets the points of the currently logged in user
    Queries the associated Player model
    Returns the user's current points if it exists, otherwise an error is returned
    """
    user = request.user
    try:
        player = Player.objects.get(user=user)
        return JsonResponse({"success": True, "score": player.points})
    except Player.DoesNotExist:
        return JsonResponse({"success": False, "error": "Player profile not found"}, status=404)

@login_required
def get_user_rank(request):
    """
    Retrieve the current user's ranking based on points
    All player are ordered in descending order of points
    Users with the same points share the same rank
    Returns the user's current rank if it exists, otherwise an error is returned
    """
    players = Player.objects.select_related('user').order_by('-points')

    current_rank = 1
    current_score = None
    same_rank_count = 0

    for index, player in enumerate(players):
        if index == 0:
            current_score = player.points
        else:
            if player.points != current_score:
                current_rank += same_rank_count
                current_score = player.points
                same_rank_count = 0

        same_rank_count += 1

        if player.user == request.user:
            return JsonResponse({"success": True, "rank": current_rank})

    return JsonResponse({"success": False, "error": "Player not found"}, status=404)


"""
renders the quiz page for users to participate in quizzes
"""
def quiz(request):
    return render(request, 'core/quiz.html')


"""
renders the profile page displaying user details
"""
def profile_view(request):
    return render(request, 'core/profile.html')
    

"""
renders the leaderboard page showcasing rankings and scores
"""   
def leaderboard_view(request):
    return render(request, 'core/leaderboard.html')
    
# View to fetch all questions from the database
def fetch_questions(request):
    """
    Randomly selected from the database for 5 questions and save the session
    Render the question page and pass the question content to the front end in JSON format
    """
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
    """
    Compare the user submitted answers to the correct answers for each question
    Accumulate points and update user points into Player model
    Save the results to session and then jump to the results page
    """
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
    """
    Get the correct number of questions, points, total points, etc., from the session
    Return the rendered results page
    """
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
    """
    Displays the walking game page, allowing users to start challenges
    """
    return render(request, 'core/walkinggame.html')

@login_required
def save_trip(request):
    """
    Saves or updates walking trip data, calculates points, and updates the player's score
    """
    if request.method == 'POST':
        session_id = request.POST.get('session_id')
        if not session_id:
            return JsonResponse({'error': 'session_id cannot be empty'}, status=400)
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')
        distance = request.POST.get('distance')
        duration = float(request.POST.get('duration')) / 1000
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
    """
    Retrieves and displays the user's walking challenge history in HTML format
    """
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
                duration_seconds = float(trip.duration)
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
def upload_avatar(request): # Upload the avatar
    """
    Only support the POST request
    Verify the file type and delete the old avatar (if it is not the default avatar)
    Save the new avatar and update the user profile
    Return the upload result and the avatar address
    """
    if request.method == "POST":
        if 'avatar' not in request.FILES:
            return JsonResponse({"success": False, "error": "No file uploaded"}, status=400, content_type="application/json")

        avatar_file = request.FILES['avatar']
        
        if not avatar_file.content_type.startswith('image/'):
            return JsonResponse({"success": False, "error": "Invalid file type"}, status=400, content_type="application/json")

        profile = get_object_or_404(Profile, user=request.user)

        if profile.avatar_url and 'avatars/' in profile.avatar_url:
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
def get_user_profile(request): # Profile page obtain user information
    """
    Return username, email, first name, last name, avatar address to the front end
    Used for front-end Profile page initialization
    """
    if request.method == "GET":
        user = request.user

        profile = get_object_or_404(Profile, user=user)
        if profile.avatar_url and 'avatars/' in profile.avatar_url:
            avatar_url = f"{settings.MEDIA_URL}{profile.avatar_url}"
        else:
            avatar_url = static('pictures/fox.jpg')
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
def get_avatar(request): # Obtain the user avatar
    """
    Obtain the user avatar for display
    If the user does not have a customized avatar, the default avatar address is returned
    """
    if request.method == "GET":
        profile = get_object_or_404(Profile, user=request.user)
        if profile.avatar_url and 'avatars/' in profile.avatar_url:
            avatar_url = f"{settings.MEDIA_URL}{profile.avatar_url}"
        else:
            avatar_url = static('pictures/fox.jpg')
        return JsonResponse({"success": True, "avatar_url": avatar_url}, content_type="application/json")
    
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405, content_type="application/json")

@login_required
def delete_account(request): # Cancel the account
    """
    Cancel the current account
    Only support the DELECT request
    Delete the user and log out, and clear the session
    """
    if request.method == "DELETE":

        user = request.user
        user.delete()
        logout(request)
        return JsonResponse({"success": True, "message": "Account deleted successfully"}, content_type="application/json")

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405, content_type="application/json")

@login_required
def update_user_profile(request): # Update the user information
    """
    Update the user's personal information
    Support the PUT request
    Users can modify information: username, email, first name, last name
    If the user changes the email, the user must log out automatically and ask to log in again using the new email
    """
    if request.method == "PUT":

        try:
            data = json.loads(request.body)
            user = request.user
            old_email = user.email
            new_email = data.get('email', user.email)

            if CustomUser.objects.filter(email=new_email).exclude(id=user.id).exists(): # Check whethe the email are duplicated
                return JsonResponse({"success": False, "error": "This email is already in use"}, status=400, content_type="application/json")

            user.username = data.get('username', user.username)
            user.email = data.get('email', user.email)
            user.first_name = data.get('first_name', user.first_name)
            user.last_name = data.get('last_name', user.last_name)

            user.save()

            email_changed = old_email != user.email
            if email_changed: # User need to log in again after changing the email
                logout(request)
                return JsonResponse({"success": True, "message": "Profile updated successfully", "email_changed": True}, content_type="application/json")
            return JsonResponse({"success": True, "message": "Profile updated successfully"}, content_type="application/json")
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400, content_type="application/json")
    
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405, content_type="application/json")

@login_required
def change_password(request): # Reset the password of the logged-in user
    """
    The logged-in user's change password
    The POST request receives the new password, verifies its validity and saves it
    Return whether the update succeeded or an error message
    """
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
def logout_view(request): # Logout
    """
    When the user logs out, the session is cleared, the cookie is deleted, and the logout success message is returned
    Only support the POST request
    """
    if request.method == "POST":

        logout(request)

        request.session.flush()
        response = JsonResponse({"success": True, "message": "Logged out successfully"}, content_type="application/json")
        response.delete_cookie("sessionid")
        response.delete_cookie("csrftoken")
        return response
    
    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405, content_type="application/json") 
    
class CustomPasswordResetView(auth_views.PasswordResetView):
    """
    Custom the password reset view
    Used to generate password reset links and send emails
    Override the form_valid method to inject a custom URL
    """
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
    """
    The user can click the reset link to set a new password
    Redirect to the custom password_reset_complete page if successful
    """
    success_url = reverse_lazy('core:password_reset_complete') 
    
def recycling_view(request):
    """
    Display all recycling stations that support QR code scanning
    Get all recycling stations and renders them to the front page
    """
    bins = RecyclingBin.objects.all()
    return render(request, 'core/recycling.html', {'bins': bins})

@login_required
def get_user_info(request):
    """
    Get user information, return the current user points and the date of the last code scan
    If the user data does not exist, an error message is displayed
    """
    try:
        player = Player.objects.get(user=request.user)
        last_scan = ScanRecord.objects.filter(user=request.user).order_by('-scan_date').first()

        last_scan_date = last_scan.scan_date.strftime('%Y-%m-%d') if last_scan else ''

        response_text = f"status=success&points={player.points}&lastScanDate={last_scan_date}"
        return HttpResponse(response_text, content_type="text/plain")
    except Player.DoesNotExist:
        return HttpResponse("status=error&message=User data not found", content_type="text/plain")

@csrf_exempt
@login_required
def scan_qr_code(request):
    """
    Code scanning in POST request mode
    Verify whether the QR code exists and whether the user has scanned the code on that station that day
    After the scanning is successful, record the scanning record, accumulate the points, and return the result
    The return format is text/plain, and contain the integral and status information
    """
    if request.method != "POST":
        return HttpResponse("status=error&message=Invalid request method", content_type="text/plain")

    user = request.user
    player, created = Player.objects.get_or_create(user=user)
    
    today = now().date()
    
    qr_code = request.POST.get("qrCode", "").strip()
    if not qr_code:
        return HttpResponse("status=invalid&message=Invalid QR code. Please try again.", content_type="text/plain")

    # check if it is the QR code in the database
    if not RecyclingBin.objects.filter(qr_code=qr_code).exists():
        return HttpResponse("status=invalid&message=Invalid QR code. Please try again.", content_type="text/plain")
    
    if ScanRecord.objects.filter(user=user, scan_date=today, qr_code=qr_code).exists(): # users can scan once per station per day
        return HttpResponse("status=already_scanned_today&message=Task completed. Please come back tomorrow.", content_type="text/plain")

    # record the scanning information
    try:
        ScanRecord.objects.create(user=user, scan_date=today, qr_code=qr_code)
    except Exception as e:
        return HttpResponse(f"status=error&message=Database error: {str(e)}", content_type="text/plain")

    points_earned = 10
    player.points += points_earned
    player.save()

    response_text = f"status=success&points={player.points}&pointsEarned={points_earned}&lastScanDate={today}"
    return HttpResponse(response_text, content_type="text/plain")

@login_required
def get_leaderboard(request):
    """
    Fetches the leaderboard data sorted by player points in descending order, 
    includes user avatars, and determines the current user's rank
    """
    players = (
        Player.objects
        .select_related('user__profile')
        .annotate(username=F('user__username'), avatar=F('user__profile__avatar_url'))
        .order_by('-points')  # sort by points in descending order
    )

    leaderboard_data = []
    for player in players:
        if player.avatar and 'avatars/' in player.avatar:
            avatar_url = request.build_absolute_uri(settings.MEDIA_URL + player.avatar)
        else:
            avatar_url = request.build_absolute_uri(static('pictures/fox.jpg'))

        leaderboard_data.append({
            "name": player.username,
            "score": player.points,
            "avatar": avatar_url
        }) 

    # calculate the current user rank
    user_rank = None
    for index, player in enumerate(leaderboard_data):
        if player["name"] == request.user.username:
            user_rank = index + 1
            break

    return JsonResponse(leaderboard_data, safe=False)