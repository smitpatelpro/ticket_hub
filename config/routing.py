from django.urls import re_path

from apps.common import consumers
from django.urls import include, path

websocket_urlpatterns = [
    path("ws/projects/<uuid:project_id>/", consumers.ProjectConsumer.as_asgi()),
]