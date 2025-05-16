from django.db import models

# Only the track model for now.
class Track(models.Model):
    label = models.CharField(max_length=100)
    # For now, I want to keep it blank, but I should probaly use NULL and check for that in the client.
    description = models.TextField(blank=True)
    url = models.FileField(upload_to='trackfiles/')
    difficulty = models.CharField(max_length=50, choices=[('facil','Fácil'), ('moderado','Moderado'), ('dificil','Difícil')], default='moderado')
    duration = models.DurationField(blank=True, null=True) # Except for these.
    route_type = models.CharField(max_length=50, choices=[('ida_volta', 'Ida e Volta'), ('ida', 'Ida'), ('volta', 'Volta')], default='ida_volta')
    elevation = models.FloatField(blank=True, null=True)
    
# And should definitely add a User model.