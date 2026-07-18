from rest_framework import serializers
from .models import FavoriteCity

class FavoriteCitySerializer(serializers.ModelSerializer):
    class Meta:
        model = FavoriteCity
        fields = '__all__'