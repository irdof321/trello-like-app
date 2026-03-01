from django.core.exceptions import PermissionDenied
from rest_framework import viewsets
from website.cardboard.serializers import BoardSerializer, ColumnSerializer
from .models import Board, Column, Card
from .serializers import CardSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser



class CardViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Card.objects.all()
    serializer_class = CardSerializer


    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Card.objects.none()
        if user.is_staff:
            return Card.objects.all()
        return  (Card.objects.filter(column__board__owner=user) | Card.objects.filter(column__board__members=user)).distinct()
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated()]
        return [IsAuthenticated()]

    def perform_update(self, serializer):
        card = self.get_object()
        user = self.request.user
        if not user.is_staff and card.assigned_to != user and card.column.board.owner != user:
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
        if user.is_staff:
            return Column.objects.all()
        return Column.objects.filter(board__owner=user) | Column.objects.filter(board__members=user)

    def perform_update(self, serializer):
        column = self.get_object()
        if not self.request.user.is_staff and (
            column.board.owner != self.request.user or
            not column.board.members.filter(id=self.request.user.id).exists()):

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
        if user.is_staff:
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
    

