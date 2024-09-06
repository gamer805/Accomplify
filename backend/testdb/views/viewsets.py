from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from ..models import List, Task, Attachment
from ..serializers import (
    ListSerializer, ListWithoutTasksSerializer,
    TaskSerializer, TaskCreateUpdateSerializer,
    AttachmentSerializer, AttachmentCreateSerializer
)
class ListViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['name', 'category']

    def get_queryset(self):
        return List.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return ListWithoutTasksSerializer
        return ListSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['title', 'description']
    filterset_fields = ['completed', 'priority', 'list']

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return TaskCreateUpdateSerializer
        return TaskSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AttachmentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Attachment.objects.all()

    def get_queryset(self):
        return Attachment.objects.filter(task__user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return AttachmentCreateSerializer
        return AttachmentSerializer

    def perform_create(self, serializer):
        task = serializer.validated_data['task']
        if task.user != self.request.user:
            self.permission_denied(self.request)
        serializer.save()