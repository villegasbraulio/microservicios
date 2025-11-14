from rest_framework import serializers
from .models import Favorite


class FavoriteSerializer(serializers.ModelSerializer):
    """Serializer para el modelo Favorite"""
    
    class Meta:
        model = Favorite
        fields = ['id', 'product_id', 'user_id', 'notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user_id', 'created_at', 'updated_at']


class FavoriteCreateSerializer(serializers.Serializer):
    """Serializer para crear un favorito"""
    product_id = serializers.CharField(max_length=255, required=True)
    notes = serializers.CharField(required=False, allow_blank=True)


class FavoriteCheckSerializer(serializers.Serializer):
    """Serializer para verificar si un producto está en favoritos"""
    is_favorite = serializers.BooleanField()
    favorite = FavoriteSerializer(required=False, allow_null=True)

