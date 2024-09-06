from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class List(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.category} - {self.name}"

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('L', 'Low'),
        ('M', 'Medium'),
        ('H', 'High'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    due_date = models.TextField(blank=True)
    task_iden = models.TextField(blank=True)
    completed = models.BooleanField(default=False)
    priority = models.CharField(max_length=1, choices=PRIORITY_CHOICES, default='M')
    
    tasklist = models.ForeignKey(List, on_delete=models.CASCADE, related_name='tasks')
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='task_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.task.title}"