from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator

# Only the track model for now.
class Track(models.Model):
    # DIFFICULTY choices
    DIFFICULTY_EASY = 'facil'
    DIFFICULTY_MODERATE = 'moderado'
    DIFFICULTY_DIFFICULT = 'dificil'
    DIFFICULTY_CHOICES = [
        (DIFFICULTY_EASY, 'Fácil'),
        (DIFFICULTY_MODERATE, 'Moderado'),
        (DIFFICULTY_DIFFICULT, 'Difícil'),
    ]
    
    # ROUTE_TYPE choices
    ROUTE_TYPE_ROUND_TRIP = 'ida_volta'
    ROUTE_TYPE_ONE_WAY = 'ida'
    ROUTE_TYPE_RETURN = 'volta'
    ROUTE_TYPE_CHOICES = [
        (ROUTE_TYPE_ROUND_TRIP, 'Ida e Volta'),
        (ROUTE_TYPE_ONE_WAY, 'Ida'),
        (ROUTE_TYPE_RETURN, 'Volta'),
    ]
    
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    url = models.FileField(upload_to='trackfiles/', validators=[FileExtensionValidator(allowed_extensions=['gpx'])])
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default=DIFFICULTY_MODERATE)
    duration = models.PositiveIntegerField(blank=True, null=True, help_text="Duration should be in minutes")
    route_type = models.CharField(max_length=10, choices=ROUTE_TYPE_CHOICES, default=ROUTE_TYPE_ROUND_TRIP)
    elevation = models.FloatField(blank=True, null=True, help_text="Elevation should be in meters")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label} ({self.url})" # I want to make sure that the track path is being properly stored.
    
# And should definitely add a User model.