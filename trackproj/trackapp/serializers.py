from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Track, Profile, Rating, Favorite, TrackImage, CommunityPost, PostComment, PostReaction

class TrackImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrackImage
        fields = ['id', 'image', 'created_at']

class TrackSerializer(serializers.ModelSerializer):
    favorites_count = serializers.SerializerMethodField()
    is_favorite = serializers.SerializerMethodField()
    image = serializers.ImageField(use_url=True, required=False, allow_null=True)
    images = TrackImageSerializer(many=True, read_only=True)

    class Meta:
        model = Track
        fields = '__all__'

    def get_favorites_count(self, obj):
        return Favorite.objects.filter(track=obj).count()

    def get_is_favorite(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user, track=obj).exists()
        return False

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(write_only=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    cpf = serializers.CharField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'name', 'phone', 'cpf']

    def create(self, validated_data):
        name = validated_data.pop('name')
        phone = validated_data.pop('phone', '')
        cpf = validated_data.pop('cpf', '')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        Profile.objects.create(user=user, name=name, phone=phone, cpf=cpf)
        return user

class ProfileSerializer(serializers.ModelSerializer):
    picture = serializers.ImageField(use_url=True, required=False, allow_null=True)

    class Meta:
        model = Profile
        fields = ['name', 'phone', 'cpf', 'picture']

class PublicProfileSerializer(serializers.ModelSerializer):
    picture = serializers.ImageField(use_url=True, read_only=True)

    class Meta:
        model = Profile
        fields = ['name', 'picture']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

class PublicUserSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='profile.name', read_only=True)
    picture = serializers.ImageField(source='profile.picture', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'name', 'picture']

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')
    user_name = serializers.ReadOnlyField(source='user.profile.name')
    user_picture = serializers.ImageField(source='user.profile.picture', read_only=True)

    class Meta:
        model = Rating
        fields = ['id', 'user', 'user_name', 'user_picture', 'track', 'comment', 'date', 'score']
        read_only_fields = ['user', 'date']

class PostCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.profile.name')
    user_picture = serializers.ImageField(source='user.profile.picture', read_only=True)
    
    class Meta:
        model = PostComment
        fields = ['id', 'user', 'user_name', 'user_picture', 'content', 'created_at']
        read_only_fields = ['user', 'created_at']

class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ['id', 'user', 'reaction_type']
        read_only_fields = ['user']

class CommunityPostSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.profile.name')
    user_picture = serializers.ImageField(source='user.profile.picture', read_only=True)
    comments = PostCommentSerializer(many=True, read_only=True)
    reactions_summary = serializers.SerializerMethodField()
    user_reaction = serializers.SerializerMethodField()
    track_info = TrackSerializer(source='track', read_only=True)
    
    class Meta:
        model = CommunityPost
        fields = ['id', 'user', 'user_name', 'user_picture', 'content', 'image', 'track', 'track_info', 'created_at', 'comments', 'reactions_summary', 'user_reaction']
        read_only_fields = ['user', 'created_at']

    def get_reactions_summary(self, obj):
        from django.db.models import Count
        return obj.reactions.values('reaction_type').annotate(count=Count('reaction_type'))

    def get_user_reaction(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                reaction = obj.reactions.get(user=request.user)
                return reaction.reaction_type
            except PostReaction.DoesNotExist:
                return None
        return None
