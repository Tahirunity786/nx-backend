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
from urllib.parse import parse_qs
logger = logging.getLogger(__name__)


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.token = self.scope['url_route']['kwargs'].get('token')
        try:
            if self.token:
                # Decode JWT token
                payload = jwt.decode(self.token, settings.SECRET_KEY, algorithms=['HS256'])
                raw_primary_user = payload.get('user_id')
    
                # Fetch primary user (anonymous user) and admin
                primary_user = await self.get_user_by_cookie(raw_primary_user)
    
                if not primary_user:
                    raise ValueError("Invalid primary user")
                
                self.group_name = f'notifications_{primary_user.id}'
                await self.channel_layer.group_add(
                    self.group_name,
                    self.channel_name
                )
                await self.accept()
            else:
                self.group_name = None  # Explicitly set group_name to None
                await self.close()
        except jwt.ExpiredSignatureError:
            await self.close()
        except jwt.InvalidTokenError:
            await self.close()
        except ValueError as e:
            await self.close()
        except Exception as e:
            await self.close()
    
    @sync_to_async
    def get_user_by_cookie(self, user_id):
        try:
            token = AnonymousCookies.objects.get(cookie=user_id)
            return token.user
        except AnonymousCookies.DoesNotExist:
            return None
        

    async def disconnect(self, close_code):
        if self.group_name:  # Check if group_name is set
            await self.channel_layer.group_discard(
                self.group_name,
                self.channel_name
            )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event['message']))



class ChatConsumer(AsyncWebsocketConsumer):


    async def connect(self):
        self.token = self.scope['url_route']['kwargs'].get('token')

        # Process for admin
        # Extract roomName from the query string
        query_string = self.scope['query_string'].decode('utf-8')
        query_params = parse_qs(query_string)
        room_name = query_params.get('roomName', [None])[0]
    

        try:
            # Decode JWT and validate user
            payload = jwt.decode(self.token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')

            if not user_id:
                raise ValueError("Invalid token payload: user_id missing")

            primary_user, is_admin, room_id = await self.get_user_by_cookie(user_id)
            if not primary_user:
                raise ValueError("Invalid primary user")
            
            if is_admin and room_name:
                secondary_user = await sync_to_async(CustomUser.objects.get)(id=room_name)

            else:
                secondary_user = await sync_to_async(CustomUser.objects.get)(admin=True)


            if not secondary_user:
                raise ValueError("Admin user not found")

            self.chatroom = self.generate_chatroom(primary_user, secondary_user)


            # Fetch or create the thread
            self.thread = await self.get_thread(primary_user, secondary_user)

            # Add user to the group and accept the connection
            await self.channel_layer.group_add(self.chatroom, self.channel_name)
            await self.accept()

            # Send chat history
            chat_history = await self.fetch_chat_history(self.thread)
            await self.send_json({
                "type": "chat_history",
                "messages": chat_history
            })

        except jwt.ExpiredSignatureError:
            await self.close()
        except jwt.InvalidTokenError:
            await self.close()
        except ValueError as e:
            await self.close()
        except Exception as e:
            await self.close()

    async def receive(self, text_data):
        try:
            message_data = json.loads(text_data)
            
            message = message_data.get('message')
            if not message:
                raise ValueError("No message content")
    
            # Decode token to fetch user ID
            payload = jwt.decode(self.token, settings.SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
    
            # Validate user and thread
            primary_user = await self.get_user_by_cookie(user_id)
            if isinstance(primary_user, tuple):
                primary_user = primary_user[0]  # Adjust if needed
    
            secondary_user = await sync_to_async(CustomUser.objects.filter(admin=True).first)()
            
            if not primary_user or not secondary_user or not self.thread:
                raise ValueError("Invalid user or thread")
    
            # Save message to the database
            user = await self.get_user(primary_user.id)
            if isinstance(user, tuple):
                user = user[0]  # Adjust if needed
    
            saved_message = await self.save_message(self.thread, user, message)
    
            # Serialize and send the message to the group
            serialized_message = ChatMessageSerializer(saved_message).data
            await self.channel_layer.group_send(
                self.chatroom,
                {
                    'type': 'chat_message',
                    'message': serialized_message
                }
            )
            notification = {
                'type': 'send_notification',
                'message': {
                    'sender': f"{user.first_name} {user.last_name}",
                    'message': message
                }
            }
            await self.channel_layer.group_send(
                f'notifications_{secondary_user.id}',
                notification
            )
    
        except (json.JSONDecodeError, ValueError) as e:
            await self.send_json({'error': str(e)})
        except Exception as e:
            await self.send_json({'error': 'Internal server error'})

    async def chat_message(self, event):
        await self.send_json(event['message'])

    async def disconnect(self, close_code):
        if hasattr(self, 'chatroom'):
            await self.channel_layer.group_discard(
                self.chatroom,
                self.channel_name
            )
    
    @staticmethod
    def generate_chatroom(user_a, user_b):
        # Sort the user IDs in ascending order
        user_ids = sorted([user_a.id, user_b.id])
    
        # Return the formatted chatroom ID string
        room_id = f"chat_{user_ids[0]}_{user_ids[1]}"
        return room_id

    @database_sync_to_async
    def fetch_chat_history(self, thread):
        messages = Chatmessage.objects.filter(thread=thread).order_by('message_time')
        return ChatMessageSerializer(messages, many=True).data

    @database_sync_to_async
    def save_message(self, thread, user, message):
        return Chatmessage.objects.create(thread=thread, user=user, message=message)

    @sync_to_async
    def get_thread(self, first_person, second_person):
        thread, _ = ChatThread.objects.get_or_create(
            primary_user=min(first_person, second_person, key=lambda u: u.id),
            secondary_user=max(first_person, second_person, key=lambda u: u.id),
        )
        return thread

    @sync_to_async
    def get_user_by_cookie(self, user_id):
        try:
            token = AnonymousCookies.objects.get(cookie=user_id)
            return token.user, token.user.admin, token.user.chat_room_id
        except AnonymousCookies.DoesNotExist:
            return None, False, None

    @sync_to_async
    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return None

    async def send_json(self, content):
        await self.send(text_data=json.dumps(content))