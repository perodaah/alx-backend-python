from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification

User = get_user_model()

class MessageNotificationTests(TestCase):
    def setUp(self):
        self.sender = User.objects.create_user(username='sender', password='x')
        self.receiver = User.objects.create_user(username='receiver', password='x')

    def test_notification_created_on_message(self):
        msg = Message.objects.create(sender=self.sender, receiver=self.receiver, content='Hello')
        self.assertEqual(Notification.objects.filter(user=self.receiver, message=msg).count(), 1)

    def test_no_duplicate_on_update(self):
        msg = Message.objects.create(sender=self.sender, receiver=self.receiver, content='Hi')
        self.assertEqual(Notification.objects.filter(message=msg).count(), 1)
        msg.content = 'Hi edited'
        msg.save()
        self.assertEqual(Notification.objects.filter(message=msg).count(), 1)
