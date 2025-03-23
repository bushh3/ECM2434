from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile, Player
from .models import Quiz, Question
from .models import RecyclingBin, ScanRecord
from .models import WalkingChallenge

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Customiza the user's display configuration in Django's background: username, email, first name, last name, and whether or not you are an administrator
    Support search by email, username, and sort by email
    """
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('email', 'username')
    ordering = ('email',)

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """
    The display configuration of the Player model in the background: username, email, points, and avatar address of the associated user
    Support search by username, email, and reverse order of points
    """
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
    """
    The display of the user's avatar is configured in the background
    """
    list_display = ['user', 'avatar_url']

@admin.register(WalkingChallenge)
class WalkingChallengeAdmin(admin.ModelAdmin):
    """
    The display configuration of the WalkingChallenge model in the background: user, start and end time, distance, whether completed, and points
    Support filter by start time and completion status
    """
    list_display = ('player', 'start_time', 'end_time', 'distance', 'is_completed', 'points_earned')    
    list_filter = ('start_time', 'is_completed')
    search_fields = ('player__user__email',)

@admin.register(RecyclingBin)
class RecyclingBinAdmin(admin.ModelAdmin):
    """
    The display configuration of recycling station in the background: location, QR code, and creation time
    """
    list_display = ('location_name', 'qr_code', 'created_at')

@admin.register(ScanRecord)
class ScanRecordAdmin(admin.ModelAdmin):
    """
    The display configuration of the ScanRecord model in the background: user, QR code, and date
    Support filter and sort by user and date
    """
    list_display = ('user', 'qr_code', 'scan_date')
    list_filter = ('user', 'scan_date')
    ordering = ('user', 'scan_date')

admin.site.register(Quiz)
admin.site.register(Question)