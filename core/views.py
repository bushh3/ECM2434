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
            return render(request, 'core/signup.html', {"error_message": "email already in use"})

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
            return render(request, 'core/signup.html', {"error_message": "an error occurred, please try again"})

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
    session_id = generate_session_id()  # implement this function to generate a unique session id
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
    # points logic, e.g., 1 point for each km
    return int(distance)

# function to calculate walking speed
def calculate_speed(lat, lng):
    # logic to calculate speed (in km/h) based on GPS data
    return 5  # return a fixed value for example, but you can calculate real speed
