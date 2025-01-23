from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<token>[a-zA-Z0-9-_\.]+)$', consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/notification/(?P<token>[a-zA-Z0-9-_\.]+)$', consumers.NotificationConsumer.as_asgi()),
]
