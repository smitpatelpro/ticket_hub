from django.urls import re_path

from apps.common import consumers
from django.urls import include, path

websocket_urlpatterns = [
    path("ws/abc", consumers.WSConsumer.as_asgi()),
    path("ws/projects/<uuid:project_id>/", consumers.ProjectConsumer.as_asgi()),
    # re_path(r"ws/(?P<room_name>\w+)/$", consumers.WSConsumer.as_asgi()),
    # re_path(r"ws/(?P<room_name>\w+)/$", consumers.ProjectConsumer.as_asgi()),
]