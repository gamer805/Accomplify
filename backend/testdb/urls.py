from django.urls import include, path
from rest_framework.routers import DefaultRouter
from .views import apis, homepage
from .views.viewsets import DatasheetViewSet, ConversationViewSet, QuestionViewSet, AnswerViewSet, ModelViewSet, ComponentViewSet

router = DefaultRouter()
router.register(r'datasheets', DatasheetViewSet, basename='datasheet')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'questions', QuestionViewSet, basename='question')
router.register(r'answers', AnswerViewSet, basename='answer')
router.register(r'models', ModelViewSet, basename='model')
router.register(r'components', ComponentViewSet, basename='component')

urlpatterns = [
    path('', homepage.home, name='home'),
    path('api/', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/upload_datasheet/', apis.upload_datasheet, name='upload_datasheet'),
    path('api/delete_datasheet/', apis.delete_datasheet, name='delete_datasheet'),
    path('api/get_datasheets', apis.get_datasheets, name='get_datasheets'),
    path('api/classify_data/', apis.classify_data, name='classify_data'),
    path('api/ask_question/', apis.ask_question, name='ask_question'),
    path('api/get_component/', apis.get_component, name='get_component'),
	path('api/get_conversation_history/', apis.get_conversations_by_datasheet, name='conversation_history'),
    path('api/add_ollama_models/', apis.add_ollama_models, name='add_ollama_models'),
    path('api/generate_data_format/', apis.generate_data_format, name='generate_data_format'),
    path('api/assign_component_info/', apis.assign_component_info, name='assign_component_info')
]