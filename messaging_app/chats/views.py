from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import User, Message, Conversation
from .serializers import UserSerializer, MessageSerializer, ConversationSerializer
from django_filters.rest_framework import DjangoFilterBackend
from .permissions import IsMessageOwner, IsParticipantOfConversation
from .auth import get_tokens_for_user
from .pagination import MessagePagination
from .filters import MessageFilter

""" class UserRegisterAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()

        token = get_tokens_for_user(user)
        response_data = {
            'user': serializer.data,
            'tokens': token
        }

        return Response(response_data, status=status.HTTP_201_CREATED) """


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('last_name', 'first_name')
    serializer_class = UserSerializer


class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = MessageFilter
    permission_classes = [IsMessageOwner, IsAuthenticated]
    pagination_class = MessagePagination

    def get_queryset(self):
        return Message.objects.filter(sender=self.request.user)


    def create(self, request, *args, **kwargs):
        conversation_id = request.data.get("conversation")
        message_body = request.data.get("message_body")

        if not conversation_id or not message_body:
            return Response({"error": "conversation and message_body are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        conversation = get_object_or_404(Conversation, conversation_id=conversation_id)
        sender = request.user

        message = Message.objects.create(
            conversation=conversation,
            sender=sender,
            message_body=message_body
        )

        serializer = self.get_serializer(message)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['participants']
    permission_classes = [IsParticipantOfConversation, IsAuthenticated]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user)

    def create(self, request, *args, **kwargs):
        user_ids = request.data.get("participants")
        if not user_ids or not isinstance(user_ids, list):
            return Response({"error": "participants must be a list of user_ids"}, status=status.HTTP_400_BAD_REQUEST)

        if request.user not in conversation.participants.all():
            return Response({"error": "You are not a participant of this conversation."}, status=status.HTTP_403_FORBIDDEN)


        conversation= Conversation.objects.create()
        conversation.participants.set(user_ids)
        conversation.save()

        serializer = self.get_serializer(conversation)
        return Response(serializer.data, status=status.HTTP_201_CREATED)



