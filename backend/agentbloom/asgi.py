"""
ASGI config for agentbloom project.
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agentbloom.settings")
django_asgi_app = get_asgi_application()

from apps.agent.routing import websocket_urlpatterns as agent_ws  # noqa: E402
from apps.receptionist.routing import websocket_urlpatterns as receptionist_ws  # noqa: E402

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(agent_ws + receptionist_ws))
        ),
    }
)
