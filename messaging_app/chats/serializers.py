from rest_framework import serializers
from .models import User, Conversation, Message


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'phone_number', 'role', 'created_at', 'password'
        ]
        read_only_fields = ['id', 'created_at', 'role']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.password_hash = user.password  # mirrors hashed password
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
            instance.password_hash = instance.password
        instance.save()
        return instance


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.PrimaryKeyRelatedField(read_only=True)
    sender_detail = UserSerializer(source='sender', read_only=True)
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all())

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_detail', 'conversation', 'message_body', 'sent_at']
        read_only_fields = ['id', 'sent_at', 'sender']


class ConversationSerializer(serializers.ModelSerializer):
    participants = serializers.PrimaryKeyRelatedField(many=True, queryset=User.objects.all())
    participants_detail = UserSerializer(source='participants', many=True, read_only=True)
    messages = MessageSerializer(many=True, required=False)
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = [
            'id', 'participants', 'participants_detail',
            'created_at', 'messages', 'message_count', 'last_message'
        ]
        read_only_fields = ['id', 'created_at']

    def get_message_count(self, obj):
        return obj.messages.count()

    def get_last_message(self, obj):
        last = obj.messages.order_by('-sent_at').first()
        return MessageSerializer(last).data if last else None

    def validate(self, attrs):
        participants = attrs.get('participants', [])
        if self.instance and not participants:
            participants = list(self.instance.participants.all())
        if len(participants) < 2:
            raise serializers.ValidationError({'participants': 'At least two participants required.'})
        msgs = attrs.get('messages', [])
        for m in msgs:
            if not m.get('message_body'):
                raise serializers.ValidationError({'messages': 'Message body cannot be blank.'})
        return attrs

    def create(self, validated_data):
        messages_data = validated_data.pop('messages', [])
        participants = validated_data.pop('participants', [])
        convo = Conversation.objects.create(**validated_data)
        if participants:
            convo.participants.set(participants)
        for msg in messages_data:
            Message.objects.create(conversation=convo, sender=self.context['request'].user, **msg)
        return convo

    def update(self, instance, validated_data):
        messages_data = validated_data.pop('messages', None)
        participants = validated_data.pop('participants', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if participants is not None:
            instance.participants.set(participants)
        if messages_data is not None:
            instance.messages.all().delete()
            for msg in messages_data:
                Message.objects.create(conversation=instance, sender=self.context['request'].user, **msg)
        return instance