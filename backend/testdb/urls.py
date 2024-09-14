from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import apis, homepage
from .views.viewsets import ListViewSet, TaskViewSet, AttachmentViewSet
from .views.apis import save_tasklist, get_tasklist, google_login

router = DefaultRouter()
router.register(r'lists', ListViewSet, basename='list')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'attachments', AttachmentViewSet, basename='attachment')

urlpatterns = [
    path('', homepage.home, name='home'),
    path('api/', include(router.urls)),
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/google-login/', apis.google_login, name='google-login'),
    path('api/save_tasklist/', apis.save_tasklist, name='save_tasklist'),
    path('api/get_tasklist/', apis.get_tasklist, name='get_tasklist')
]
