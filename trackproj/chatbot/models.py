import uuid
from django.db import models
from django.contrib.auth.models import User

class ChatRoom(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, related_name='messages', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username}: {self.content}'

    class Meta:
        ordering = ('timestamp',)

class KnowledgeBase(models.Model):
    """
    Stores static text entered directly via Admin.
    """
    title = models.CharField(max_length=255)
    content = models.TextField()
    
    # Links this row to a specific Point ID in Qdrant for updates/deletion
    qdrant_id = models.UUIDField(null=True, blank=True, unique=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Document(models.Model):
    """
    Stores uploaded files (PDFs, etc) to be processed by Gemini.
    """
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    
    # Links this file to a specific Point ID in Qdrant
    qdrant_id = models.UUIDField(null=True, blank=True, unique=True)
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)

    def __str__(self):
        return self.title