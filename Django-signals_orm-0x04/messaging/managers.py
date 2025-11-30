from django.db import models

class UnreadMessagesManager(models.Manager):
    def unread_for_user(self, user):
        """
        Return unread messages for a specific user.
        """
        return self.filter(receiver=user, read=False)
    
    
