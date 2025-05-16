from django.contrib import admin
from .models import Track

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('label', 'difficulty', 'duration', 'route_type', 'url')
    search_fields = ('label', 'description')
    list_filter = ('difficulty', 'route_type')
