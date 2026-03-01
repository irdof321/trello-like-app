from rest_framework import serializers
from .models import Board, Column, Card
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff']

class CardSerializer(serializers.ModelSerializer):
    
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Card
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        user = request.user
        card = self.instance
        if not card or not hasattr(card, 'column'):
            return fields
        
        if  card and card.column.board.owner == user:
            return fields
        elif card and card.column.board.members.filter(id=user.id).exists():
            fields['title'].read_only = True
            fields['assigned_to'].read_only = True
            return fields
        
        return fields


class ColumnSerializer(serializers.ModelSerializer):
    
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Column
        fields = '__all__'

    def get_fields(self):
        fields = super().get_fields()
        column = self.instance
        request = self.context.get('request')
        user = request.user

        if not column or not hasattr(column, 'board'):
            return fields
        
        if  column and column.board.owner == user:
            return fields
        elif column and column.board.members.filter(id=user.id).exists():
            fields['name'].read_only = True
            fields['owner'].read_only = True
            return fields
        
        return fields


class BoardSerializer(serializers.ModelSerializer):
    
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Board
        fields = '__all__'


    def get_fields(self):
        fields = super().get_fields()
        board = self.instance
        request = self.context.get('request')
        user = request.user

        if not board or not hasattr(board, 'owner'):
            return fields
        
        if board and board.owner == user:
            return fields
        elif board and board.members.filter(id=user.id).exists():
            fields['name'].read_only = True
            fields['owner'].read_only = True
            fields['members'].read_only = True
            return fields
        
        return fields
    