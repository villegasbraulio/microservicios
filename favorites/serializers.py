from rest_framework import serializers


class FavoriteCreateSerializer(serializers.Serializer):
    product_id = serializers.CharField(max_length=255, required=True)
    notes = serializers.CharField(required=False, allow_blank=True)

