import uuid
from django.db import models
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

class Track(models.Model):
    # DIFFICULTY
    DIFFICULTY_EASY = 'facil'
    DIFFICULTY_MODERATE = 'moderado'
    DIFFICULTY_DIFFICULT = 'dificil'
    DIFFICULTY_CHOICES = [
        (DIFFICULTY_EASY, 'Fácil'),
        (DIFFICULTY_MODERATE, 'Moderado'),
        (DIFFICULTY_DIFFICULT, 'Difícil'),
    ]
    
    # ROUTE_TYPE
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
    distance = models.FloatField(validators=[MinValueValidator(0.0)], blank=True, null=True, help_text="Distance should be in meters")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default=DIFFICULTY_MODERATE)
    duration = models.PositiveIntegerField(blank=True, null=True, help_text="Duration should be in minutes")
    route_type = models.CharField(max_length=10, choices=ROUTE_TYPE_CHOICES, default=ROUTE_TYPE_ROUND_TRIP)
    elevation = models.FloatField(blank=True, null=True, help_text="Elevation should be in meters")
    image = models.ImageField(upload_to='tracks/images/', blank=True, null=True)

    qdrant_id = models.UUIDField(null=True, blank=True, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.label} ({self.url})"

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    cpf = models.CharField(max_length=14, blank=True, null=True)
    picture = models.ImageField(upload_to='profile/', blank=True, null=True)

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

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    track = models.ForeignKey(Track, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'track')
    
    def __str__(self):
        return f"{self.user.username} - {self.track.label}"

class TrackImage(models.Model):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='tracks/gallery/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.track.label}"

class CommunityPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    image = models.ImageField(upload_to='community/posts/', blank=True, null=True)
    track = models.ForeignKey(Track, on_delete=models.SET_NULL, null=True, blank=True, related_name='mentioned_in_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by {self.user.username} at {self.created_at}"

class PostComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.id}"

class PostReaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('love', 'Love'),
        ('haha', 'Haha'),
        ('wow', 'Wow'),
        ('sad', 'Sad'),
        ('angry', 'Angry'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reactions')
    post = models.ForeignKey(CommunityPost, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')

    def __str__(self):
        return f"{self.user.username} reacted {self.reaction_type} to {self.post.id}"