from rest_framework import serializers
from seed import board
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

        
        if user.is_superuser:
            return data

        # Create
        if card is None:
            column = data.get('column')
            board = column.board if column else None
            assigned_to = data.get('assigned_to')

        # Update
        elif hasattr(card, 'column'):
            column = data.get('column', card.column)
            board = column.board if column else None
            assigned_to = data.get('assigned_to', card.assigned_to)

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
        print(f"data keys: {data.keys()}, assigned_to in data: {'assigned_to' in data}, value: {data.get('assigned_to')}")
        if "assigned_to" in data and data.get("assigned_to") is not None:
            print(f"Validating assignment change: user={user}, board.owner={board.owner}, assigned_to={assigned_to}")
            if user != board.owner:
                raise serializers.ValidationError(
                    {"assigned_to": "Only the board owner can assign a card."}
                )
            assigned_to = data.get("assigned_to")

            # Check if assigned user is a member of the board
            if assigned_to != board.owner and not board.members.filter(id=assigned_to.id).exists():
                raise serializers.ValidationError(
                    {"assigned_to": "Assigned user is not a member of this board."}
                )
            
        # Only board owner and assigned user can change the status and priority
        if card and ("status" in data or "priority" in data) and user != board.owner and assigned_to != user:
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
    cards = CardSerializer(many=True, read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = Column
        fields = '__all__'

    def validate(self, data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        
        if user.is_superuser:
            return data

        column = self.instance

        # Create
        if column is None:
            board = data.get('board')
        # Update
        elif hasattr(column, 'board'):
            board = data.get('board', column.board)
        else:
            return data

        if not board:
            return data

        if not (user == board.owner or user.is_superuser):
            raise serializers.ValidationError(
                {"board": "Only the board owner can add columns."}
            )
        
        if column and "board" in data and data["board"] != column.board:
            raise serializers.ValidationError(
                {"board": "You cannot move a column to another board."}
            )
        
        return data

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

    def validate(self, data):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        
        if user.is_superuser:
            return data

        # Only staff can be owner
        if "owner" in data and not data["owner"].is_staff:
            raise serializers.ValidationError(
                {"owner": "Board owner must be a staff user."}
            )

        # Members cannot be the owner at the same time
        if "members" in data and "owner" in data:
            if data["owner"] in data["members"]:
                raise serializers.ValidationError(
                    {"members": "Owner cannot be in the members list."}
                )

        return data

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
    