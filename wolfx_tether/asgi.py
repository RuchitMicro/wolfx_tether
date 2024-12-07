"""
ASGI config for wolfx_tether project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import django

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application

# 1. Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wolfx_tether.settings')

# 2. Initialize Django
django.setup()

# 3. Import routing after Django setup
from web.routing import websocket_urlpatterns

# 4. Get Django's ASGI application to handle HTTP requests
django_asgi_app = get_asgi_application()

# 5. Define the ASGI application with both HTTP and WebSocket protocols
application = ProtocolTypeRouter({
    "http": django_asgi_app,  # Handles traditional HTTP requests
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns  # Handles WebSocket connections
        )
    ),
})
