# from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from .models import Track
from .serializers import TrackSerializer

# For now, the project should only need a way to extract track data (and its GPX files)
# without any authentication. 
class TrackViewSet(ModelViewSet):
    queryset = Track.objects.all()
    serializer_class = TrackSerializer

# Should definitely add a sign-in/sign-up though.