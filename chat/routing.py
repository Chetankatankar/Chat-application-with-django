
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer.as_asgi()),
]

# This file batata hai ki kis path pr konsa consumer handle krega 
# Without this file connection establish nhi hotaa