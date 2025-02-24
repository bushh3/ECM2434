"""
author: Anna Mackay, Zhiqiao Luo
"""

from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', include('core.urls')),
    path('admin/', admin.site.urls),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
]
