from django.shortcuts import render
from rest_framework import viewsets, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from .filters import MessageFilter
from rest_framework.exceptions import PermissionDenied

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .permissions import IsParticipantOfConversation

# Create your views here.


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['participants']  # ?participants=<user_id>
    search_fields = ['messages__message_body']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        # Return only conversations where the requesting user is a participant
        return Conversation.objects.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        convo = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(self.get_serializer(convo).data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], url_path='messages')
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        data = {
            'conversation': str(conversation.id),
            'message_body': request.data.get('message_body', '')
        }
        msg_serializer = MessageSerializer(data=data, context={'request': request})
        msg_serializer.is_valid(raise_exception=True)
        msg = msg_serializer.save(sender=request.user)
        return Response(MessageSerializer(msg).data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [IsParticipantOfConversation]
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter

    def get_queryset(self):
        # Restrict messages to those in conversations the user participates in
        conversation_id = self.kwargs.get('conversation_pk') or self.kwargs.get('conversation_id') or self.request.query_params.get('conversation_id')
        base_qs = Message.objects.filter(conversation__participants=self.request.user)
        if conversation_id:
            base_qs = base_qs.filter(conversation_id=conversation_id)
        return base_qs

    def list(self, request, *args, **kwargs):
        conversation_id = self.kwargs.get('conversation_pk') or request.query_params.get('conversation_id')
        if conversation_id:
            # Ensure user is participant before listing messages
            if not Conversation.objects.filter(id=conversation_id, participants=request.user).exists():
                return Response({"detail": "Forbidden"}, status=status.HTTP_403_FORBIDDEN)
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        conversation = serializer.validated_data.get('conversation')
        if not conversation.participants.filter(id=self.request.user.id).exists():
            raise PermissionDenied("Not a participant of this conversation.")
        serializer.save(sender=self.request.user)

    def perform_update(self, serializer):
        conversation = serializer.instance.conversation
        if not conversation.participants.filter(id=self.request.user.id).exists():
            raise PermissionDenied("Not a participant of this conversation.")
        serializer.save()

    def perform_destroy(self, instance):
        if not instance.conversation.participants.filter(id=self.request.user.id).exists():
            raise PermissionDenied("Not a participant of this conversation.")
        instance.delete()
