from django.urls import path, include
from rest_framework.routers import DefaultRouter
from views.viewsets import CategoryViewSet, ListViewSet, TaskViewSet, AttachmentViewSet
from views.apis import save_task

router = DefaultRouter()
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'lists', ListViewSet, basename='list')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'attachments', AttachmentViewSet, basename='attachment')

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/save_task/', apis.save_task, name='save_task')
]

# If you want to see the API endpoints in the browsable API
from rest_framework.documentation import include_docs_urls

urlpatterns += [
    path('api/docs/', include_docs_urls(title='Accomplify API')),
]