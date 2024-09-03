from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Category, List, Task, Attachment
from .serializers import (
    CategorySerializer, CategoryWithoutListsSerializer,
    ListSerializer, ListWithoutTasksSerializer,
    TaskSerializer, TaskCreateUpdateSerializer,
    AttachmentSerializer, AttachmentCreateSerializer
)

class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name']
    filterset_fields = ['name']

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return CategoryWithoutListsSerializer
        return CategorySerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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

    @action(detail=False, methods=['get'])
    def overdue(self, request):
        overdue_tasks = self.get_queryset().filter(is_overdue=True)
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)

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