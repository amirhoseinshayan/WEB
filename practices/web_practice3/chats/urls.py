from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AIModelViewSet,
    AssistantViewSet,
    ConversationMessagesAPIView,
    ConversationViewSet,
    MessageViewSet,
    ProjectConversationsAPIView,
    ProjectViewSet,
)


app_name = 'chats'


router = DefaultRouter()
router.register(r'projects', ProjectViewSet, basename='project')
router.register(r'models', AIModelViewSet, basename='ai-model')
router.register(r'assistants', AssistantViewSet, basename='assistant')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')


urlpatterns = [
    path('', include(router.urls)),
    path(
        'projects/<int:project_id>/conversations/',
        ProjectConversationsAPIView.as_view(),
        name='project-conversations',
    ),
    path(
        'conversations/<int:conversation_id>/messages/',
        ConversationMessagesAPIView.as_view(),
        name='conversation-messages',
    ),
]