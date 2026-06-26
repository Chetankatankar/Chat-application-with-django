
import json
import urllib.parse
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from firebase_admin import firestore 

from chatproject import firebase_config  

# helper - runs blocking firestore add in sync wrapper
@sync_to_async
def push_message_firestore(room_name, sender, message):
    try:
        client = firebase_config.get_firestore_client()
        # collection path: rooms/{room_name}/messages/{auto-id}
        messages_coll = client.collection("rooms").document(room_name).collection("messages")
        # add doc with server timestamp
        messages_coll.add({
            "sender": sender,
            "message": message,
            "timestamp": firestore.SERVER_TIMESTAMP
        })
    except Exception as e:
        print("Firestore push error:", e)

@sync_to_async
def save_message_mysql_sync(room_obj, sender, message):
    # if you also want to save in Django MySQL via ORM synchronously:
    from .models import Message
    Message.objects.create(room=room_obj, sender=sender, message=message)

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        raw_room = self.scope['url_route']['kwargs'].get('room_name', 'unknown')
        self.room_name = urllib.parse.unquote(raw_room)
        self.room_group_name = f'chat_{self.room_name}'
        print(f"[ChatConsumer] connect attempt for room: {self.room_name}")
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()
        print(f"[ChatConsumer] accepted connection for {self.room_name}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        print(f"[ChatConsumer] disconnected {self.room_name} (code={close_code})")

    async def receive(self, text_data):
        # parse incoming JSON
        try:
            data = json.loads(text_data)
        except Exception as exc:
            print("[ChatConsumer] invalid json:", exc, "raw:", text_data)
            return

        message = data.get('message')
        sender = data.get('sender', 'anon')
        if not message:
            print("[ChatConsumer] empty message ignored")
            return

        print(f"[ChatConsumer] recv from {sender} in {self.room_name}: {message!r}")

    
        room_obj = None
        try:
            from .models import Room
            room_obj = await sync_to_async(Room.objects.get)(room_name=self.room_name)
        except Exception:
            room_obj = None

        # Save to MySQL (if you want) - call wrapped save
        if room_obj is not None:
            await save_message_mysql_sync(room_obj, sender, message)

        # Save to Firestore (async wrapper)
        await push_message_firestore(self.room_name, sender, message)

        # create a client-side friendly timestamp string (immediate)
        timestamp_str = datetime.utcnow().strftime("%I:%M %p")  

        # broadcast to group (so all clients get it)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
                'timestamp_str': timestamp_str,
            }
        )

    async def chat_message(self, event):
        # send event to WebSocket
        await self.send(text_data=json.dumps({
            'message': event.get('message'),
            'sender': event.get('sender'),
            'timestamp': event.get('timestamp_str'),
        }))
