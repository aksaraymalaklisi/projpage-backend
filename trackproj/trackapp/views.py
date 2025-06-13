# Django (pale in comparison to the imports right after it)
from django.contrib.auth.models import User

# Rest Framework paraphernalia
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers as drf_serializers
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly, IsAuthenticated, 
    AllowAny
)
from rest_framework.exceptions import PermissionDenied

# Models and Serializers
from .models import Track, Profile, Rating, Favorite
from .serializers import (
    TrackSerializer, UserRegisterSerializer, UserSerializer, 
    ProfileSerializer, RatingSerializer
)

class TrackViewSet(ModelViewSet):
    queryset = Track.objects.all().order_by('id')
    serializer_class = TrackSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        track = self.get_object()
        user = request.user
        favorite, created = Favorite.objects.get_or_create(user=user, track=track)
        if not created:
            favorite.delete()
            favorited = False
        else:
            favorited = True
        count = Favorite.objects.filter(track=track).count()
        return Response({'favorited': favorited, 'favorites_count': count})

class UserRegisterViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method in ['PUT', 'PATCH']:
            profile_serializer = ProfileSerializer(user.profile, data=request.data, partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
                return Response(UserSerializer(user).data)
            return Response(profile_serializer.errors, status=400)
        return Response(UserSerializer(user).data)

class RatingViewSet(ModelViewSet):
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy', 'create']:
            return [IsAuthenticated()]
        return [AllowAny()]

    def perform_create(self, serializer):
        track = serializer.validated_data['track']
        if Rating.objects.filter(user=self.request.user, track=track).exists():
            raise drf_serializers.ValidationError('Você já avaliou esta trilha.')
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        if serializer.instance.user != self.request.user:
            raise PermissionDenied('Você só pode editar suas próprias avaliações.')
        serializer.save()

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied('Você só pode apagar suas próprias avaliações.')
        instance.delete()