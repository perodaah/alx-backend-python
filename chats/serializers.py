from rest_framework import serializers
from .models import User, Conversation, Message

# -------------------
# User Serializer
# -------------------
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)  # CharField example

    class Meta:
        model = User
        fields = [
            'user_id', 'first_name', 'last_name', 'full_name', 'email',
            'phone_number', 'role', 'created_at'
        ]
        read_only_fields = ['user_id', 'created_at', 'full_name']


# -------------------
# Message Serializer
# -------------------
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    message_preview = serializers.SerializerMethodField()  # SerializerMethodField example

    class Meta:
        model = Message
        fields = ['message_id', 'conversation', 'sender', 'message_body', 'message_preview', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']

    def get_message_preview(self, obj):
        # Returns first 50 chars as a preview
        return obj.message_body[:50]


# -------------------
# Conversation Serializer
# -------------------
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = serializers.SerializerMethodField()  # Nested messages with method field

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']

    def get_messages(self, obj):
        # Get all messages in this conversation
        messages = obj.messages.all().order_by('sent_at')
        return MessageSerializer(messages, many=True).data


# -------------------
# nested relationship for creating conversation
# -------------------
class ConversationCreateSerializer(serializers.ModelSerializer):
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True
    )

    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participant_ids', 'created_at']
        read_only_fields = ['conversation_id', 'created_at']

    def create(self, validated_data):
        participants = validated_data.pop('participant_ids', None)
        if not participants:
            raise serializers.ValidationError("At least one participant is required.")  # ValidationError example
        conversation = Conversation.objects.create(**validated_data)
        conversation.participants.set(participants)
        return conversation

