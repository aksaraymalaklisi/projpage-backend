from rest_framework.viewsets import ModelViewSet
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Track
from .serializers import TrackSerializer

# For now, the project should only need a way to extract track data (and its GPX files)
# without any authentication. 
class TrackViewSet(ModelViewSet):
    queryset = Track.objects.all().order_by('id')
    serializer_class = TrackSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

# !!!: Should definitely add a sign-in/sign-up.