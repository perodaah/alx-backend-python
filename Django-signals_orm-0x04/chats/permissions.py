from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Allows access only to participants of a conversation.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # For Conversation objects
        if hasattr(obj, 'participants'):
            is_participant = request.user in obj.participants.all()
            if request.method in {'PUT', 'PATCH', 'DELETE'}:
                return is_participant  # Only participants can modify/delete
            return is_participant  # Participants can view
        # For Message objects
        if hasattr(obj, 'conversation'):
            is_participant = request.user in obj.conversation.participants.all()
            if request.method in {'PUT', 'PATCH', 'DELETE'}:
                return is_participant
            return is_participant  # View/send restricted to participants
        return False
