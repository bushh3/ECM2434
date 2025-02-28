"""
author: Anna Mackay
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .models import Quiz, Question

admin.site.register(Quiz)
admin.site.register(Question)