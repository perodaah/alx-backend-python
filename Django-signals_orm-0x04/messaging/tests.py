from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

User = get_user_model()

class MessageNotificationTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username='alice', password='pass')
        self.bob = User.objects.create_user(username='bob', password='pass')

    def test_notification_created_on_message(self):
        # no notifications initially
        self.assertEqual(Notification.objects.count(), 0)

        # alice sends a message to bob
        msg = Message.objects.create(sender=self.alice, receiver=self.bob, content='Hello Bob')

        # after message creation, a notification should exist for bob
        notifications = Notification.objects.filter(user=self.bob)
        self.assertEqual(notifications.count(), 1)

        n = notifications.first()
        self.assertEqual(n.actor, self.alice)
        self.assertEqual(n.message, msg)
        self.assertFalse(n.is_read)
        self.assertIn('sent you a message', n.verb)


class MessageEditHistoryTest(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user(username='alice', password='pass')
        self.bob = User.objects.create_user(username='bob', password='pass')
        # create initial message
        self.msg = Message.objects.create(sender=self.alice, receiver=self.bob, content='Original content')

    def test_history_created_when_message_edited(self):
        # no history yet
        self.assertEqual(MessageHistory.objects.filter(message=self.msg).count(), 0)

        # change content and set the transient editor attribute
        self.msg._editor = self.alice
        self.msg.content = 'Edited content'
        self.msg.save()

        # now there should be one history entry with old content
        histories = MessageHistory.objects.filter(message=self.msg)
        self.assertEqual(histories.count(), 1)
        h = histories.first()
        self.assertEqual(h.old_content, 'Original content')
        self.assertEqual(h.editor, self.alice)

        # message should be marked edited
        self.msg.refresh_from_db()
        self.assertTrue(self.msg.edited)
        self.assertIsNotNone(self.msg.last_edited_at)
        self.assertEqual(self.msg.last_edited_by, self.alice)
