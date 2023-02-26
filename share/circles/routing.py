from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/<uuid:room_name>/', consumers.ChatConsumer.as_asgi()),
]