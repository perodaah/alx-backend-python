from django.db import models
from django.contrib.auth import get_user_model
from .managers import UnreadMessagesManager
# Create your models here.

User = get_user_model()

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    parent_message = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='replies',
        on_delete=models.CASCADE
    )
    objects = models.Manager()  # default manager
    unread = UnreadMessagesManager()  # custom manager for unread messages
    def __str__(self):
        return f"Message #{self.pk} from {self.sender.username} to {self.receiver.username}"

    def __str__(self):
        return f"Message from {self.sender} to {self.receiver} at {self.timestamp}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')  # recipient
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications_sent', null=True, blank=True)
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    verb = models.CharField(max_length=255)  # short human readable description, e.g. "sent you a message"
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user}: {self.verb}"
    

class MessageHistory(models.Model):
    """
    Stores prior versions of a Message (the snapshot before an edit).
    """
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='history')
    old_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    #editor = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='edit_histories')
    edited_at = models.DateTimeField(auto_now_add=True)
    edited_by = models.ForeignKey(
        User,
        null=True,              # <-- FIX: allows existing rows to have NULL
        blank=True,             # <-- FIX: form/admin side
        on_delete=models.SET_NULL,
        related_name='edited_histories'
    )
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"History for Message #{self.message_id} at {self.created_at}"
    