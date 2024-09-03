from rest_framework import serializers
from .models import Category, List, Task, Attachment
from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']

class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'uploaded_at']

class TaskSerializer(serializers.ModelSerializer):
    attachments = AttachmentSerializer(many=True, read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'date_created', 'due_date', 
                  'completed', 'priority', 'list', 'user', 'attachments', 'is_overdue']
        read_only_fields = ['date_created', 'user']

class ListSerializer(serializers.ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = List
        fields = ['id', 'name', 'category', 'user', 'tasks']
        read_only_fields = ['user']

class CategorySerializer(serializers.ModelSerializer):
    lists = ListSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'user', 'lists']
        read_only_fields = ['user']

class CategoryWithoutListsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'user']
        read_only_fields = ['user']

class ListWithoutTasksSerializer(serializers.ModelSerializer):
    class Meta:
        model = List
        fields = ['id', 'name', 'category', 'user']
        read_only_fields = ['user']

class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'due_date', 'completed', 'priority', 'list']

    def create(self, validated_data):
        user = self.context['request'].user
        return Task.objects.create(user=user, **validated_data)

class AttachmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = ['id', 'file', 'task']

    def create(self, validated_data):
        return Attachment.objects.create(**validated_data)