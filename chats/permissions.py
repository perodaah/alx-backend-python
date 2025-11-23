from rest_framework import permissions

class IsParticipant(permissions.BasePermission):
    """
    Allow access only to conversation participants.
    """

    def has_object_permission(self, request, view, obj):
        # obj could be Conversation or Message
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # If obj is a Conversation
        if hasattr(obj, 'participants'):
            return obj.participants.filter(pk=user.pk).exists()

        # If obj is a Message, check message.conversation participants
        if hasattr(obj, 'conversation'):
            return obj.conversation.participants.filter(pk=user.pk).exists()

        return False
