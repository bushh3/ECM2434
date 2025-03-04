from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import Quiz, Question

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('email',)

admin.site.register(Quiz)
admin.site.register(Question)