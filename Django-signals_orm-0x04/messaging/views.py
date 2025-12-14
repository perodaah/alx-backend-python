from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from .models import Message
from .serializers import MessageSerializer, MessageHistorySerializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

# Create your views here.

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_user(request):
    # Explicitly delete related messages before deleting the user
    Message.objects.filter(sender=request.user).delete()
    Message.objects.filter(receiver=request.user).delete()
    request.user.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()  # cascades Messages, Notifications, MessageHistory
        return Response(status=status.HTTP_204_NO_CONTENT)

class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()  # default; overridden by get_queryset
    serializer_class = MessageSerializer

    @method_decorator(cache_page(60), name='list')
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        return (
            Message.unread.unread_for_user(user)
            .select_related('sender', 'receiver')
            .only('id', 'sender', 'receiver', 'content', 'timestamp')
        )

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)

    @action(detail=True, methods=['get'])
    def history(self, request, pk=None):
        message = self.get_object()
        ser = MessageHistorySerializer(message.history.all(), many=True)
        return Response(ser.data)

    @action(detail=True, methods=['get'])
    def thread(self, request, pk=None):
        """
        Returns the recursive threaded conversation for this message.
        """
        message = self.get_object()
        return Response(message.build_thread())
