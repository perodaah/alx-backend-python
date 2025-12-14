from django.apps import AppConfig
from django.contrib import admin


class MessagingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'messaging'

    def ready(self):
        from . import signals  # noqa

admin.site.site_header = "Messaging Administration"
admin.site.site_title = "Messaging Admin Portal"
admin.site.index_title = "Welcome to the Messaging Admin Portal"