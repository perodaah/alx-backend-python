from django.db import models
from django.contrib.auth import get_user_model
import uuid
from django.utils import timezone
from .managers import UnreadMessagesManager

User = get_user_model()

class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    read = models.BooleanField(default=False)
    edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    edited_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        related_name='message_edits',
        on_delete=models.SET_NULL
    )
    # NEW: self-referential parent for replies
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    # Managers
    objects = models.Manager()
    unread = UnreadMessagesManager()

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['receiver', 'timestamp']),
            models.Index(fields=['parent_message', 'timestamp']),  # optimize reply lookups
            models.Index(fields=['receiver', 'read', 'timestamp']),
        ]

    def __str__(self):
        return f'Msg {self.id} from {self.sender} to {self.receiver}'

    def build_thread(self):
        """
        Returns a nested dict of this message and all replies (recursive).
        Uses prefetch to reduce DB hits.
        """
        # Prime replies and related users in one go
        qs = Message.objects.filter(id=self.id).prefetch_related(
            models.Prefetch(
                'replies',
                queryset=Message.objects.all()
                    .select_related('sender', 'receiver', 'parent_message')
                    .prefetch_related('history', 'notifications')
                    .order_by('timestamp')
            )
        ).select_related('sender', 'receiver', 'parent_message')
        root = qs.first() or self

        def serialize(msg):
            return {
                'id': str(msg.id),
                'sender_id': str(msg.sender_id),
                'receiver_id': str(msg.receiver_id),
                'content': msg.content,
                'timestamp': msg.timestamp,
                'edited': msg.edited,
                'parent_message_id': str(msg.parent_message_id) if msg.parent_message_id else None,
                'replies': [serialize(child) for child in msg.replies.all()]
            }

        return serialize(root)

class Notification(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    message = models.ForeignKey(Message, related_name='notifications', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'read', 'timestamp']),
        ]

    def __str__(self):
        return f'Notification {self.id} to {self.user} (read={self.read})'


class MessageHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    message = models.ForeignKey(Message, related_name='history', on_delete=models.CASCADE)
    previous_content = models.TextField()
    logged_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-logged_at']
        indexes = [
            models.Index(fields=['message', 'logged_at']),
        ]

    def __str__(self):
        return f'History {self.id} for Message {self.message_id}'


from django.db.models.signals import pre_save
from django.dispatch import receiver

@receiver(pre_save, sender=Message)
def create_message_history(sender, instance, **kwargs):
    if instance.pk:  # Message instance is being updated
        try:
            old_instance = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            old_instance = None

        if old_instance and old_instance.content != instance.content:
            # Content has changed, create a MessageHistory entry
            MessageHistory.objects.create(
                message=instance,
                previous_content=old_instance.content
            )
            # Update edited metadata
            instance.edited = True
            instance.edited_at = timezone.now()
            instance.edited_by = instance.sender  # Assuming the sender is the one editing
