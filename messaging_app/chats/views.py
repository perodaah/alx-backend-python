from django.http import HttpResponse
from rest_framework import viewsets, filters, status
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend


from chats.models import User, Conversation, Message
from chats.serializers import (
    UserCreateSerializer,
    UserSerializer, 
    ConversationSerializer, 
    MessageSerializer
)


def index(request): 
    """
    Render the index page for the chat application.
    """   
    return HttpResponse("<h1>Welcome to the Chat Application!</h1>")


class UserViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for handling user-related operations.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['role']
    search_fields = ['email', 'username', 'first_name', 'last_name']


    def list(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({"message": "List of users", "data": serializer.data})

    def create(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()  # This will call create_user() and hash the password
            output_serializer = UserSerializer(user)
            return Response({
                "message": "User created successfully",
                "data": output_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ConversationViewSet(viewsets.ViewSet):
    """
    ViewSet for listing and creating conversations.
    """

    def list(self, request):
        conversations = Conversation.objects.all()
        serializer = ConversationSerializer(conversations, many=True)
        return Response({"message": "List of conversations", "data": serializer.data})

    def create(self, request):
        serializer = ConversationSerializer(data=request.data)
        if serializer.is_valid():
            conversation = serializer.save()
            print(f"Conversation created: {conversation}")
            return Response({"message": "Conversation created", "data": serializer.data}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageViewSet(viewsets.ViewSet):
    """
    ViewSet for listing and sending messages.
    """
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['conversation', 'sender']
    search_fields = ['content']

    def list(self, request, conversation_pk=None):
        """
        Optionally filter messages by conversation.
        """
        if conversation_pk:
            messages = Message.objects.filter(conversation_id=conversation_pk)
        else:
            messages = Message.objects.all()

        serializer = MessageSerializer(messages, many=True)
        return Response({"message": "List of messages", "data": serializer.data})

    def create(self, request, conversation_pk=None):
        """
        Send a new message in a specific conversation.
        """
        data = request.data.copy()
        if conversation_pk:
            data['conversation'] = conversation_pk

        serializer = MessageSerializer(data=data)
        if serializer.is_valid():
            message = serializer.save()
            return Response({
                "message": "Message sent",
                "data": MessageSerializer(message).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
