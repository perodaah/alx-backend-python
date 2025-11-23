from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings

# Create your models here.

class User(AbstractUser):
    USER_ROLES = [
        ('guest', 'Guest'),
        ('host', 'Host'),
        ('admin', 'Admin'),
    ]

    user_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=150, null=False)
    last_name = models.CharField(max_length=150, null=False)
    email = models.EmailField(unique=True, null=False)
    #password_hash = models.CharField(max_length=128, null=False)  # store hashed password
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(max_length=10, choices=USER_ROLES, default='guest', null=False)
    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'  # make email the login field
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def __str__(self):
        return f"{self.email} ({self.role})"
    

class Conversation(models.Model):
    conversation_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    participants = models.ManyToManyField(User, related_name='conversations')
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Conversation {self.conversation_id}"
    

class Message(models.Model):
    message_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    message_body = models.TextField(null=False)
    sent_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Message {self.message_id} by {self.sender.email}"

