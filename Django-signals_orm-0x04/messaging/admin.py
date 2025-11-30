from django.contrib import admin
from .models import Message, Notification, MessageHistory
# Register your models here.


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'sender', 'receiver', 'timestamp', 'read')
    list_filter = ('timestamp', 'read')
    search_fields = ('sender__username', 'receiver__username', 'content')

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'actor', 'verb', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'actor__username', 'verb')

@admin.register(MessageHistory)
class MessageHistoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'message', "edited_at", "edited_by")
    readonly_fields = ('old_content', 'created_at')
    search_fields = ('message__id', 'editor__username', 'old_content')

