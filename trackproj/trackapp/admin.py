from django.contrib import admin, messages
from django.utils.html import format_html
from .models import Track, Profile, Rating, Favorite
from chatbot.utils import sync_item_to_qdrant

# Chatbot knowledge sync function
def force_sync_tracks(modeladmin, request, queryset):
    """
    Manually sends selected tracks to Qdrant via the utility function.
    """
    count = 0
    errors = 0
    for item in queryset:
        try:
            sync_item_to_qdrant(item)
            count += 1
        except Exception as e:
            errors += 1
            modeladmin.message_user(request, f"Error syncing '{item.label}': {e}", messages.ERROR)
            
    if count > 0:
        modeladmin.message_user(request, f"Successfully synced {count} tracks to Qdrant.", messages.SUCCESS)

force_sync_tracks.short_description = "Force Update Vector DB"

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    
    # Show preview image 
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;"/>', obj.image.url)
        return ''
    image_tag.short_description = 'Image'

    # Added 'qdrant_id' to the end of the list so the admin can see sync status
    list_display = ('label', 'difficulty', 'duration', 'distance', 'route_type', 'image_tag', 'url', 'id', 'qdrant_id')
    
    search_fields = ('label', 'description')
    list_filter = ('difficulty', 'route_type')
    
    # Add the action button
    actions = [force_sync_tracks]

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'phone', 'cpf', 'picture')
    search_fields = ('name', 'cpf', 'user__username')

@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('user', 'track', 'score', 'date')
    search_fields = ('user__username', 'track__label')
    list_filter = ('score', 'date')

@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'track')
    search_fields = ('user__username', 'track__label')