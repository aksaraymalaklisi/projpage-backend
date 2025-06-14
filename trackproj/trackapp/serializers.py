from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Track, Profile, Rating, Favorite

class TrackSerializer(serializers.ModelSerializer):
    favorites_count = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = '__all__'

    def get_favorites_count(self, obj): # Uma Track pode ter seus favoritos acessados.
        return Favorite.objects.filter(track=obj).count() # Tecnicamente, isso não faz parte do modelo.

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

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

class RatingSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.id')

    class Meta:
        model = Rating
        fields = ['id', 'user', 'track', 'comment', 'date', 'score']
        read_only_fields = ['user', 'date']
