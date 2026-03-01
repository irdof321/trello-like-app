from rest_framework import serializers
from .models import Board, Column, Card

class CardSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Card
        fields = 'title', 'content', 'status', 'priority', 'assigned_to', 'created_at', 'updated_at', 'column', 'order'

    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    