from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Player
from .models import Quiz, Question

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('email',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'get_email', 'points', 'get_avatar')
    search_fields = ('user__email', 'user__username')
    ordering = ('-points',)

    def get_username(self, obj):
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    def get_avatar(self, obj):
        return obj.user.profile.avatar_url

    get_username.short_description = "Username"
    get_email.short_description = "Email"
    get_avatar.short_description = "Avatar URL"

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'avatar_url']

admin.site.register(Quiz)
admin.site.register(Question)