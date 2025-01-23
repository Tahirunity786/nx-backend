import json
import jwt
from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.db.models import Q
import logging
from core_control.models import AnonymousCookies
from core_message.serializers import ChatMessageSerializer
from .models import ChatThread, Chatmessage, CustomUser

logger = logging.getLogger(__name__)


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Extract the token from the URL
        self.token = self.scope['url_route']['kwargs'].get('token')

        try:
            # Decode JWT token
            payload = jwt.decode(self.token, settings.SECRET_KEY, algorithms=['HS256'])
            raw_primary_user = payload.get('user_id')
            print(raw_primary_user)

            # Fetch primary user (anonymous user) and admin (secondary user)
            primary_user = await self.get_user_by_cookie(raw_primary_user)
            secondary_user = await sync_to_async(CustomUser.objects.get)(admin=True)

            if not primary_user or not secondary_user:
                raise ValueError("Invalid primary or secondary user")

            # Use the admin's ID to determine the chatroom name
            self.chatroom = f'chatroom_admin_{secondary_user.id}'

            # Add the user (primary or admin) to the same chatroom group
            await self.channel_layer.group_add(
                self.chatroom,
                self.channel_name
            )
            await self.accept()

            print(f"User {primary_user.id if primary_user else 'Admin'} connected to chatroom: {self.chatroom}")

        except jwt.ExpiredSignatureError:
            print("Token expired")
            await self.close()
        except jwt.InvalidTokenError:
            print("Invalid token")
            await self.close()
        except CustomUser.DoesNotExist:
            print("Admin user not found")
            await self.close()
        except Exception as e:
            print(f"Error during connection: {e}")
            await self.close()

    async def receive(self, text_data):
        try:
            message_data = json.loads(text_data)
            print(message_data)
            message = message_data.get('message')

            if not message:
                raise ValueError("No message content")

            # Decode JWT token to fetch user ID
            payload = jwt.decode(self.token, settings.SECRET_KEY, algorithms=['HS256'])
            raw_primary_user = payload.get('user_id')

            # Fetch primary user and admin
            primary_user = await self.get_user_by_cookie(raw_primary_user)
            secondary_user = await sync_to_async(CustomUser.objects.get)(admin=True)

            # Fetch or create the chat thread
            thread = await self.get_thread(primary_user, secondary_user)
            if not primary_user or not secondary_user or not thread:
                raise ValueError("Invalid user or thread")

            # Save the message to the database
            user = await self.get_user(primary_user.id)
            saved_message = await self.save_message(thread, user, message)

            # Serialize and send the message to the group
            serialized_message = ChatMessageSerializer(saved_message).data
            
            await self.channel_layer.group_send(
                self.chatroom,
                {
                    'type': 'chat_message',
                    'message': serialized_message
                }
            )
            print(f"Message sent to group {self.chatroom}: {serialized_message}")
        except (json.JSONDecodeError, ValueError) as e:
            await self.send(text_data=json.dumps({'error': str(e)}))
        except Exception as e:
            print(f"Unexpected error: {e}")
            await self.send(text_data=json.dumps({'error': 'Internal server error'}))

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event['message']))

    async def disconnect(self, close_code):
        # Remove the user from the chatroom group
        if hasattr(self, 'chatroom'):
            await self.channel_layer.group_discard(
                self.chatroom,
                self.channel_name
            )
            print(f"User disconnected from chatroom: {self.chatroom}")

    @database_sync_to_async
    def save_message(self, thread, user, message):
        return Chatmessage.objects.create(thread=thread, user=user, message=message)

    @sync_to_async
    def get_thread(self, first_person, second_person):
        # Fetch the existing thread between these two users
        thread = ChatThread.objects.filter(
            Q(primary_user=first_person, secondary_user=second_person) |
            Q(primary_user=second_person, secondary_user=first_person)
        ).first()
    
        # If no thread exists, create a new one
        if not thread:
            # Ensure a single thread is created for these users
            thread, created = ChatThread.objects.get_or_create(
                primary_user=min(first_person, second_person, key=lambda u: u.id),
                secondary_user=max(first_person, second_person, key=lambda u: u.id),
            )
        
        return thread

    @sync_to_async
    def get_user_by_cookie(self, cookie):
        try:
            token = AnonymousCookies.objects.get(cookie=cookie)
            return token.user
        except AnonymousCookies.DoesNotExist:
            return None

    @sync_to_async
    def get_user(self, user_id):
        return CustomUser.objects.filter(id=user_id).first()
