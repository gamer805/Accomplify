from django.contrib import admin
from .models import Category, List, Task, Attachment

class AttachmentInline(admin.TabularInline):
    model = Attachment
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')
    search_fields = ('name', 'user__username')
    list_filter = ('user',)

@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'user')
    list_filter = ('category', 'user')
    search_fields = ('name', 'category__name', 'user__username')

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'list', 'user', 'due_date', 'completed', 'priority', 'is_overdue')
    list_filter = ('completed', 'priority', 'list', 'user')
    search_fields = ('title', 'description', 'list__name', 'user__username')
    date_hierarchy = 'due_date'
    inlines = [AttachmentInline]

    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'list', 'user')
        }),
        ('Status', {
            'fields': ('completed', 'priority')
        }),
        ('Dates', {
            'fields': ('due_date',)
        }),
    )

    def is_overdue(self, obj):
        return obj.is_overdue
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue'

@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ('task', 'file', 'uploaded_at')
    list_filter = ('uploaded_at', 'task__list')
    search_fields = ('task__title', 'file')