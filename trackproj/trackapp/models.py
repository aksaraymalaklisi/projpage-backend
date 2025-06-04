from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

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
    url = models.FileField(upload_to='tracks/', validators=[FileExtensionValidator(allowed_extensions=['gpx'])])
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default=DIFFICULTY_MODERATE)
    duration = models.PositiveIntegerField(blank=True, null=True, help_text="Duration should be in minutes")
    route_type = models.CharField(max_length=10, choices=ROUTE_TYPE_CHOICES, default=ROUTE_TYPE_ROUND_TRIP)
    elevation = models.FloatField(blank=True, null=True, help_text="Elevation should be in meters")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label} ({self.url})" # I want to make sure that the track path is being properly stored.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)

    def __str__(self):
        return self.name or self.user.username

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    class Meta:
        unique_together = ('user', 'track')
        ordering = ['-date']

    def __str__(self):
        return f"{self.user.username} - {self.track.label} ({self.score})"