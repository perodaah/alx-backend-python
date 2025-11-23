from django.contrib import admin
from .models import User, Conversation, Message
# Register your models here.

admin.site.register(User)
admin.site.register(Conversation)
admin.site.register(Message)