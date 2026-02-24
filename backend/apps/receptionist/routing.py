from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(
        r"ws/receptionist/(?P<embed_key>[0-9a-f]+)/$",
        consumers.ReceptionistConsumer.as_asgi(),
    ),
]
