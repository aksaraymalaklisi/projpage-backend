"""
ASGI config for trackproj project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application

# 1. Set the settings module FIRST, before importing any Django tools.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trackproj.settings')

# 2. Initialize the Django ASGI application early.
# This triggers 'django.setup()', which loads your settings and models.
django_asgi_app = get_asgi_application()

# 3. NOW it is safe to import your project routing.
# These imports access models, so they must happen AFTER the lines above.
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chatbot.routing

application = ProtocolTypeRouter({
    # Serve HTTP requests using the Django application initialized above
    "http": django_asgi_app,
    
    # Serve WebSocket requests using Channels
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chatbot.routing.websocket_urlpatterns
        )
    ),
})