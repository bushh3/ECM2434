from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Player
from .models import Quiz, Question
from .models import WalkingChallenge

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('email',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('user', 'points')
    search_fields = ('user__email',)
    ordering = ('-points',)

@admin.register(WalkingChallenge)
class WalkingChallengeAdmin(admin.ModelAdmin):
    list_display = ('player', 'start_time', 'end_time', 'distance', 'is_completed', 'points_earned')    
    list_filter = ('start_time', 'is_completed')
    search_fields = ('player__user__email',)

admin.site.register(Quiz)
admin.site.register(Question)