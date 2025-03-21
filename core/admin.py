from django.contrib import admin

from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Player
from .models import Quiz, Question
from .models import RecyclingBin, ScanRecord

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

@admin.register(RecyclingBin)
class RecyclingBinAdmin(admin.ModelAdmin):
    list_display = ('location_name', 'qr_code', 'created_at')

@admin.register(ScanRecord)
class ScanRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'qr_code', 'scan_date')
    list_filter = ('user', 'scan_date')
    ordering = ('user', 'scan_date')

admin.site.register(Quiz)
admin.site.register(Question)