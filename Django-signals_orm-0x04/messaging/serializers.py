from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Message, MessageHistory, Notification


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['sender', 'receiver', 'content', 'edited', 'timestamp']


class MessageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageHistory
        fields = ['message', 'content', 'edited_by', 'edited_at']


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['notification_id', 'recipient', 'sender', 'message', 'is_read']