from django.db import models

class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        qs = (
            self.get_queryset()
            .filter(receiver=user, read=False)
        )
        # Return minimal fields for inbox listing
        return qs.only('id', 'sender', 'receiver', 'content', 'timestamp')
