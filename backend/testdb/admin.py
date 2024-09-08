from django.contrib import admin
from .models import AccomplifyUser, List, Task, Attachment

@admin.register(AccomplifyUser)
class AccomplifyUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'given_name')
    search_fields = ('email', 'name', 'given_name')

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'user')
    list_filter = ('category', 'user')
    search_fields = ('name', 'category', 'user__email', 'user__name')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'tasklist', 'user', 'due_date', 'task_iden', 'completed', 'priority')
    list_filter = ('completed', 'priority', 'tasklist', 'user')
    search_fields = ('title', 'description', 'tasklist__name', 'user__email', 'user__name')
    inlines = [AttachmentInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'due_date', 'task_iden', 'tasklist', 'user')
        }),
        ('Status', {
            'fields': ('completed', 'priority')
        }),
    )

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'file', 'uploaded_at')
    list_filter = ('uploaded_at', 'task__tasklist')
    search_fields = ('task__title', 'file')