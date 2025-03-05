from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.db.models import F
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
import random
from django.utils import timezone

# login view
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
            return render(request, "core/login.html", {"form": form})

# sign up view
def signup(request):
    if request.POST == {}:
        return render(request, 'core/signup.html')
    else:
        username = request.POST['username']
        email = request.POST['email']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        password = request.POST['password']

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'core/signup.html', {"error_message": "Email already in use"})

        try:
            user = CustomUser.objects.create_user(
                username=username, email=email, first_name=first_name, last_name=last_name, password=password
            )
            user.save()

            player = Player(user=user)
            player.save()

            authenticated_user = authenticate(username=username, password=password)

            if authenticated_user:
                login(request, authenticated_user)
            return HttpResponseRedirect('/home/')
        
        except IntegrityError:
            return render(request, 'core/signup.html', {"error_message": "An error occurred, please try again"})

# home view
def home(request):
    if request.user.is_authenticated:
        return render(request, 'core/navpage2.html')
    else:
        return HttpResponseRedirect('/login/')

# profile view
def profile_view(request):
    return render(request, 'core/profile.html')

# walking challenge: start new walking trip
@login_required
def start_walking(request):
    player = request.user.player
    session_id = 'session_' + str(timezone.now().timestamp())  # Generate a unique session ID
    start_time = timezone.now()

    trip = WalkingTrip.objects.create(
        player=player,
        session_id=session_id,
        start_time=start_time,
        distance=0,
        duration=0,
        is_completed=False,
        points_earned=0,
        track_points_count=0
    )

    return HttpResponse(f"success, session_id={session_id}")

# save walking trip data
@login_required
def save_trip_data(request):
    if request.method == "POST":
        session_id = request.POST.get('session_id')
        trip = WalkingTrip.objects.get(session_id=session_id)

        # update trip details (end_time, distance, etc.)
        trip.end_time = timezone.now()
        trip.distance = float(request.POST.get('distance', 0))
        trip.duration = int(request.POST.get('duration', 0))
        trip.is_completed = True
        trip.points_earned = calculate_points(trip.distance)

        # save the track points
        track_points_count = int(request.POST.get('track_points_count', 0))
        for i in range(track_points_count):
            lat = float(request.POST.get(f'point_lat_{i}', 0))
            lng = float(request.POST.get(f'point_lng_{i}', 0))
            timestamp = request.POST.get(f'point_time_{i}', None)
            WalkingTrackPoint.objects.create(
                trip=trip,
                lat=lat,
                lng=lng,
                timestamp=timestamp,
                speed=calculate_speed(lat, lng)
            )

        # update player points
        trip.player.points += trip.points_earned
        trip.player.save()

        return HttpResponse(f"success, points_earned={trip.points_earned}")

# view to fetch walking history
@login_required
def get_walk_history(request):
    player = request.user.player
    trips = WalkingTrip.objects.filter(player=player).order_by('-start_time')  # get the walking history

    history_html = "<ul>"
    for trip in trips:
        history_html += f"<li>Session: {trip.session_id}, Distance: {trip.distance} km, Points: {trip.points_earned}, Completed: {trip.is_completed}</li>"
    history_html += "</ul>"

    return HttpResponse(history_html)

# view to delete walking trip data
@login_required
def delete_trip(request):
    if request.method == "POST":
        session_id = request.POST.get('session_id')
        trip = WalkingTrip.objects.get(session_id=session_id)
        
        # delete the walking trip and related track points
        trip.delete()

        return HttpResponse("success, trip deleted")

# function to calculate points based on distance
def calculate_points(distance):
    return int(distance)  # 1 point per km

# function to calculate walking speed
def calculate_speed(lat, lng):
    return 5  # Placeholder, can be adjusted based on GPS data for actual speed

# quiz view (added this for your requirement)
def quiz(request):
    # Return the quiz page, or dynamically load questions if needed
    return render(request, 'core/quiz.html')

# view to fetch quiz questions (not used in original, but added for clarity)
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
    request.session.modified = True

    return render(request, 'core/questions.html', {'questions': selected_questions})

# view to check the user's answer for a specific question
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
                correct_option = session_questions.get(question_index, {}).get('correct_option')
                if correct_option and user_answer == correct_option:
                    correct += 1
                else:
                    wrong += 1
        
        current_score = correct * score_per_question
        player = request.user.player
        player.points += current_score
        player.save()

        request.session['quiz_result'] = {
            'correct': correct,
            'wrong': wrong,
            'current_score': current_score,
            'total_score': player.points
        }
        request.session.modified = True

        return HttpResponseRedirect(reverse('core:get_quiz_results'))

# view to get the quiz results
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
    
    result_text = f"Correct: {correct}, Wrong: {wrong}, Score this time: {current_score}, Total score: {total_score}"
    
    return render(request, 'core/result.html', {'result_text': result_text})
