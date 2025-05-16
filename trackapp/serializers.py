from rest_framework import serializers
from .models import Track

class TrackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        # !!!: Should specify fields explicitly later.
        fields = '__all__'
