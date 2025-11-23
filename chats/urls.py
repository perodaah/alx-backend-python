from rest_framework import routers
from django.urls import path, include
from .views import ConversationViewSet, MessageViewSet
from rest_framework_nested import routers as nested_routers

router = routers.DefaultRouter()
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')

# Nested router for messages under a conversation
nested_router = nested_routers.NestedDefaultRouter(router, r'conversations', lookup='conversation')
nested_router.register(r'messages', MessageViewSet, basename='conversation-messages')

urlpatterns = [
    path('', include(router.urls)),           # /conversations/ and /messages/
    path('', include(nested_router.urls)),    # /conversations/<id>/messages/
]
