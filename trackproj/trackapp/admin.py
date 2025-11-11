from django.contrib import admin
from django.utils.html import format_html
from .models import Track, Profile, Rating, Favorite

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    
    # Mostrar imagem na tabela
    def image_tag(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:50px;"/>', obj.image.url)
        return ''
    image_tag.short_description = 'Image'

    list_display = ('label', 'difficulty', 'duration', 'distance', 'route_type', 'image_tag', 'url', 'id')
    search_fields = ('label', 'description')
    list_filter = ('difficulty', 'route_type')

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