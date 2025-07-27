from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter
from django.urls import path, include
from chats.views import index, UserViewSet, ConversationViewSet, MessageViewSet

# Root router
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'conversations', ConversationViewSet, basename='conversation')

# Nested router: messages under conversations
conversation_router = NestedDefaultRouter(router, r'conversations', lookup='conversation')
conversation_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', index, name='index'),
    path('', include(router.urls)),
    path('', include(conversation_router.urls)),
]
