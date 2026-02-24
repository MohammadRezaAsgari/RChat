from django.urls import re_path
from core import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/chat/(?P<chat_uuid>[0-9a-f-]{36})/$", consumers.ChatConsumer.as_asgi()
    ),
]
