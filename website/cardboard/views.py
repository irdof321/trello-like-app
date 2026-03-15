from django.core.exceptions import PermissionDenied
from rest_framework import viewsets
from website.cardboard.serializers import BoardSerializer, ColumnSerializer
from .models import Board, Column, Card, Status, Priority
from .serializers import CardSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.decorators import api_view

@api_view(['GET'])
def card_choices(request):
    return Response({
        'status': Status.choices,
        'priority': Priority.choices,
    })

class CardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Card.objects.all()
    serializer_class = CardSerializer


    def get_queryset(self):
        user = self.request.user
        
        # 1. First we filter cards based on the user's access to the board (owner or member)
        if user.is_superuser:
            queryset = Card.objects.all()
        else:
            queryset = (Card.objects.filter(column__board__owner=user) | 
                        Card.objects.filter(column__board__members=user)).distinct()
        
        # 2. Then we apply the optional column filter from query params
        column_id = self.request.query_params.get('column')
        if column_id:
            queryset = queryset.filter(column=column_id)
        
        return queryset
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        card = self.get_object()
        user = self.request.user
        if not (user.is_superuser or user.is_staff or card.assigned_to != user or card.column.board.owner != user):
            raise PermissionDenied("You are not assigned to this card.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_staff and instance.column.board.owner != user:
            raise PermissionDenied("You cannot delete this card.")
        instance.delete()



        

class ColumnViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Column.objects.all()
    serializer_class = ColumnSerializer

    def get_queryset(self):
        user = self.request.user
        
        # 1. First we filter columns based on the user's access to the board (owner or member)
        if user.is_superuser:
            queryset = Column.objects.all()
        else:
            queryset = (Column.objects.filter(board__owner=user) | Column.objects.filter(board__members=user)).distinct()
        
        # 2. Then we apply the optional board filter from query params
        board_id = self.request.query_params.get('board')
        if board_id:
            queryset = queryset.filter(board=board_id)
        
        return queryset.distinct()

    def perform_update(self, serializer):
        column = self.get_object()
        if not self.request.user.is_staff and (
            column.board.owner != self.request.user or
            not column.board.members.filter(id=self.request.user.id).exists()):

            raise PermissionDenied("You are not the owner of this Board.")
        
        serializer.save()

    def perform_create(self, serializer):
        board = Board.objects.get(pk=self.request.data["board"])
        if board.owner != self.request.user:
            raise PermissionDenied("You are not the owner of this Board.")
        
        serializer.save()
        

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_staff and instance.board.owner != user:
            raise PermissionDenied("You cannot delete this card.")
        instance.delete()
        
    
class BoardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get_queryset(self):
        user = self.request.user
        print(f"User: {self.request.user}, is_superuser: {self.request.user.is_superuser}")
        if user.is_superuser:
            return Board.objects.all()
        return Board.objects.filter(owner=user) | Board.objects.filter(members=user)
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAdminUser()]
        return [IsAuthenticated()]
    
    def perform_update(self, serializer):
        board = self.get_object()
        if not self.request.user.is_staff and board.owner != self.request.user:
            raise PermissionDenied("You are not the owner of this Board.")
        serializer.save()

    def perform_destroy(self, instance):
        user = self.request.user
        if not user.is_staff and instance.owner != user:
            raise PermissionDenied("You cannot delete this board.")
        instance.delete()

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    

