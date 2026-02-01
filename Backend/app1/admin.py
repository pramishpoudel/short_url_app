from django.contrib import admin
from .models import ShortURL, Profile


@admin.register(ShortURL)
class ShortURLAdmin(admin.ModelAdmin):
    list_display = ('key','owner','original_url','clicks','created_at','expires_at')
    search_fields = ('key','original_url','owner__username')


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user','phone','address','created_at')
