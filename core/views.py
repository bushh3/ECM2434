from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db.models import F
from .models import *
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login
from django.db import IntegrityError
# Create your views here.

# delete this later
"""
def login(request):
    if request.POST == {}:
        return render(request, "core/login.html")
    else:
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, email=email, password=password)
        if user is not None:
           login(request, user)
           print('successful?')
           return HttpResponseRedirect("core:home")
            #Redirect to home page
        else:
            #return an invalid login error message
            return render(request, 
                          "core/login.html",
                          {"error_message": "Invalid details: please try again"})
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
    
def questions(request):
    return render(request, 'core/questions.html')