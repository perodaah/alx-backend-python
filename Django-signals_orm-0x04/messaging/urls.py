from django.urls import path, include
from . import views


urlpatterns = [
    path('messaging/', include('messaging.urls')),
    path('delete_user/', views.delete_user, name='delete_user'),
    path('messages/', views.user_messages, name='user_messages'),
    path('unread_messages/', views.unread_messages_view, name='unread_messages'), 

]

