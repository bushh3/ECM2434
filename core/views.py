from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.db.models import F
from .models import *

from django.contrib.auth import authenticate
# Create your views here.

