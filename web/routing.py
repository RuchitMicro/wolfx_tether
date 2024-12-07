from django.urls import path
from .consumer import SSHConsumer

websocket_urlpatterns = [
    path('ws/ssh/<int:host_id>/', SSHConsumer.as_asgi()),
]
