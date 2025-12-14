from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

# Custom User model
class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)  # user_id
    email = models.EmailField(unique=True, db_index=True)
    phone_number = models.CharField(max_length=32, null=True, blank=True)
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='guest')
    # Optional separate password_hash if explicitly required (Django already stores hashed password in `password`)
    password_hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    username = models.CharField(max_length=150, unique=True, blank=True, null=True)

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']
    USERNAME_FIELD = 'username'  # or switch to email if desired

    def save(self, *args, **kwargs):
        # Keep password_hash synced with Django's password field
        if self.password and self.password_hash != self.password:
            self.password_hash = self.password
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email}"

    class Meta:
        indexes = [
            models.Index(fields=['email']),
        ]


# Conversation model
class Conversation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)  # conversation_id
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation {self.id}"

    class Meta:
        indexes = [
            models.Index(fields=['id']),
        ]


# Message model
class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, db_index=True)  # message_id
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    message_body = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Msg {self.id} by {self.sender_id}"

    class Meta:
        ordering = ['-sent_at']
        indexes = [
            models.Index(fields=['sender']),
            models.Index(fields=['conversation']),
        ]
