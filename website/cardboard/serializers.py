from rest_framework import serializers
from .models import Board, Column, Card
from django.contrib.auth import get_user_model

User = get_user_model()



class CardSerializer(serializers.ModelSerializer):
    
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Card
        fields = '__all__'

    def validate(self, data):
        request = self.context.get("request")
        user = getattr(request, "user", None)

        card = self.instance
        card = self.instance

        # Create
        if card is None:
            column = data.get('column')
            board = column.board if column else None

        # Update
        elif hasattr(card, 'column'):
            column = data.get('column', card.column)
            board = column.board if column else None

        # List - no validation needed
        else:
            return data

        if not board:
            return data

        # if column is being changed, check permissions on the new board
        if "column" in data:
            new_board = data["column"].board
            if user != new_board.owner and not new_board.members.filter(id=user.id).exists():
                raise serializers.ValidationError({"column": "You cannot move a card to a board you are not a member of."})



        # Only owner  can change assignment
        if "assigned_to" in data and data.get("assigned_to") is not None:
            if user != board.owner:
                raise serializers.ValidationError(
                    {"assigned_to": "Only the board owner can assign a card."}
                )
            assigned_to = data.get("assigned_to")

            # Check if assigned user is a member of the board
            if not board.members.filter(id=assigned_to.id).exists():
                raise serializers.ValidationError(
                    {"assigned_to": "Assigned user is not a member of this board."}
        )
            
        # Only board owner and assigned user can change the status and priority
        if ("status" in data or "priority" in data) and user != board.owner and card.assigned_to != user:
            raise serializers.ValidationError({"status": "Only the board owner and assigned user can change status or priority."})

        return data

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        user = request.user
        card = self.instance
        if not card or not hasattr(card, 'column'):
            return fields

        board = card.column.board

        if board.owner == user:
            return fields

        if board.members.filter(id=user.id).exists():
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
    