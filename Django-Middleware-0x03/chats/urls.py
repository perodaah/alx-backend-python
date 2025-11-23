from rest_framework import routers
from django.urls import path, include
from .views import ConversationViewSet, MessageViewSet

# Main router
router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Manually define nested URL: /conversations/<conversation_id>/messages/
conversation_messages = MessageViewSet.as_view({
    'get': 'list',
    'post': 'create'
})


urlpatterns = [
    path('', include(router.urls)),  # /conversations/ and /messages/
    path('conversations/<int:conversation_pk>/messages/', conversation_messages, name='conversation-messages'),
]
