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
from .models import Track, Profile, Rating, Favorite, CommunityPost, PostComment, PostReaction
from .serializers import (
    TrackSerializer, UserRegisterSerializer, UserSerializer, 
    ProfileSerializer, RatingSerializer, CommunityPostSerializer,
    PostCommentSerializer, PostReactionSerializer, PublicUserSerializer
)

class TrackViewSet(ModelViewSet):
    queryset = Track.objects.all().order_by('id')
    serializer_class = TrackSerializer
    pagination_class = PageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = Track.objects.all().order_by('id')
        favorited = self.request.query_params.get('favorited')
        if favorited == 'true' and self.request.user.is_authenticated:
            queryset = queryset.filter(favorite__user=self.request.user)
        return queryset

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

class CommunityPostViewSet(ModelViewSet):
    queryset = CommunityPost.objects.all()
    serializer_class = CommunityPostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = PageNumberPagination

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def comment(self, request, pk=None):
        post = self.get_object()
        serializer = PostCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post', 'delete'], permission_classes=[IsAuthenticated])
    def react(self, request, pk=None):
        post = self.get_object()
        user = request.user

        if request.method == 'DELETE':
            PostReaction.objects.filter(user=user, post=post).delete()
            return Response({'status': 'removed'})

        reaction_type = request.data.get('reaction_type')
        if not reaction_type:
            return Response({'error': 'reaction_type required'}, status=400)

        reaction, created = PostReaction.objects.update_or_create(
            user=user, post=post,
            defaults={'reaction_type': reaction_type}
        )
        return Response(PostReactionSerializer(reaction).data)

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
        if self.action in ['retrieve', 'list']:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    def get_permissions(self):
        if self.action == 'retrieve':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_serializer_class(self):
        if self.action == 'retrieve' and (not self.request.user.is_authenticated or self.request.user.id != int(self.kwargs.get('pk', 0))):
            return PublicUserSerializer
        return UserSerializer

    @action(detail=False, methods=['get', 'put', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        if request.method in ['PUT', 'PATCH']: # Essa view agora retorna o contexto do request, já que o frontend espera a requisição contendo o FQDN no path dos ImageField.
            profile_serializer = ProfileSerializer(user.profile, data=request.data, context={'request': request}, partial=True)
            if profile_serializer.is_valid():
                profile_serializer.save()
                return Response(UserSerializer(user, context={'request': request}).data)
            return Response(profile_serializer.errors, status=400)
        return Response(UserSerializer(user, context={'request': request}).data)

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

class PostCommentViewSet(ModelViewSet):
    queryset = PostComment.objects.all()
    serializer_class = PostCommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return PostComment.objects.all()

    def perform_create(self, serializer):
        # Comments are created via the nested endpoint in CommunityPostViewSet, 
        # but if we wanted to allow direct creation, we'd need to handle post assignment.
        # For now, this is mainly for delete/update.
        serializer.save(user=self.request.user)

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied('Você só pode apagar seus próprios comentários.')
        instance.delete()