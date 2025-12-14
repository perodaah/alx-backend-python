import django_filters
from .models import Message

class MessageFilter(django_filters.FilterSet):
    # Keep query param names created_after/created_before but map to sent_at
    created_after = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')
    user = django_filters.UUIDFilter(method='filter_user')  # User has UUID primary key

    def filter_user(self, queryset, name, value):
        # Messages sent by user OR in conversations the user participates in
        return queryset.filter(sender_id=value) | queryset.filter(conversation__participants__id=value)

    class Meta:
        model = Message
        fields = [
            'conversation',
            'sender',
            'sent_at',  # use existing field
        ]
