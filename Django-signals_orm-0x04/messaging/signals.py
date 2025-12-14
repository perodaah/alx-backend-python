from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.auth import get_user_model
from .models import Message, Notification, MessageHistory

@receiver(post_save, sender=Message)
def create_notification_on_message(sender, instance, created, **kwargs):
    if not created:
        return
    Notification.objects.create(user=instance.receiver, message=instance)

@receiver(pre_save, sender=Message)
def log_message_history(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        previous = Message.objects.get(pk=instance.pk)
    except Message.DoesNotExist:
        return
    if previous.content != instance.content:
        MessageHistory.objects.create(
            message=previous,
            previous_content=previous.content,
        )
        editor = getattr(instance, 'editor_override', None)
        instance.edited = True
        instance.edited_at = timezone.now()
        if editor and getattr(editor, 'is_authenticated', False):
            instance.edited_by = editor

@receiver(post_delete, sender=get_user_model())
def cleanup_user_related(sender, instance, **kwargs):
    # Explicit cleanup (CASCADE already handles most relations)
    Message.objects.filter(sender=instance).delete()
    Message.objects.filter(receiver=instance).delete()
    Notification.objects.filter(user=instance).delete()
    MessageHistory.objects.filter(message__sender=instance).delete()
    MessageHistory.objects.filter(message__receiver=instance).delete()