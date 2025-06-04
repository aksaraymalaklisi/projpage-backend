from django.contrib import admin
from .models import Track, Profile, Rating

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('label', 'difficulty', 'duration', 'route_type', 'url')
    search_fields = ('label', 'description')
    list_filter = ('difficulty', 'route_type')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone', 'cpf')
    search_fields = ('name', 'cpf', 'user__username')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'track', 'score', 'date')
    search_fields = ('user__username', 'track__label')
    list_filter = ('score', 'date')
