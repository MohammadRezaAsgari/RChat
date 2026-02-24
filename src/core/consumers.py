import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from channels.db import database_sync_to_async


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_uuid = self.scope["url_route"]["kwargs"]["chat_uuid"]
        self.room_group_name = f"chat_{self.chat_uuid}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data["message"]
        user = self.scope["user"]

        # Save message to database
        await self.save_message(user, message)

        # Broadcast message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {"type": "chat_message", "message": message, "user": user.username},
        )

    async def chat_message(self, event):
        message = event["message"]
        user = event["user"]

        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message": message, "user": user}))

    @database_sync_to_async
    def save_message(self, user, message):
        from core.models import Chat, Message

        chat = get_object_or_404(Chat, uuid=self.chat_uuid)
        return Message.objects.create(chat=chat, sender=user, content=message)
