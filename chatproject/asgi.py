
import os
from django.core.asgi import get_asgi_application

# ensure firebase initializes early
try:
    import chatproject.firebase_config  # noqa: F401
except Exception as e:
    print("Warning: firebase init failed:", e)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "chatproject.settings")

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing 

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
