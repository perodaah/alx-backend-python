from rest_framework import serializers
from .models import Message, MessageHistory

class MessageHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageHistory
        fields = ['id', 'previous_content', 'logged_at']


class ReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'timestamp', 'parent_message']
        read_only_fields = ['id', 'timestamp']


class MessageSerializer(serializers.ModelSerializer):
    history = MessageHistorySerializer(many=True, read_only=True)
    parent_message = serializers.PrimaryKeyRelatedField(queryset=Message.objects.all(), required=False, allow_null=True)
    replies = ReplySerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ['id', 'sender', 'receiver', 'content', 'created_at', 'timestamp', 'edited',
                  'parent_message', 'history', 'replies']
        read_only_fields = ['id', 'created_at', 'timestamp', 'edited', 'sender']

    def update(self, instance, validated_data):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            instance.editor_override = request.user
        return super().update(instance, validated_data)