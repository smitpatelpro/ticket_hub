import json

from channels.generic.websocket import WebsocketConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from apps.v1.projects.models import Project
from django.core.serializers.json import DjangoJSONEncoder


class WSConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))


class ProjectConsumer(AsyncWebsocketConsumer):
    """
    AsyncWebsocketConsumer to handle real-time updates for a specific project.
    Users connect to a project-specific channel layer group.
    Handles task creation, updates, comments, and user activity within the project.
    """

    async def connect(self):
        """
        Handles WebSocket connection requests.
        Authenticates the user and checks project membership.
        """
        # Get the project ID from the URL route kwargs
        # Ensure the URL pattern in routing.py captures this as 'project_id'
        self.project_id = self.scope["url_route"]["kwargs"]["project_id"]

        # Create a group name for this project
        # Group names can only contain ASCII letters, numbers, hyphens, and underscores.
        self.project_group_name = f"project_{self.project_id}"

        # Get the user from the scope (authenticated by your JWT middleware)
        user = self.scope["user"]

        # Check if the user is authenticated and is a member of the project
        if user.is_authenticated and await self.is_project_member(
            user, self.project_id
        ):
            # if user.is_authenticated:
            # Add the user's channel to the project group
            await self.channel_layer.group_add(
                self.project_group_name, self.channel_name
            )

            # Accept the WebSocket connection
            await self.accept()
            print(
                f"WebSocket connected: User {user.username} ({user.id}) joined project group {self.project_group_name}"
            )

        else:
            # If not authenticated or not a project member, close the connection
            print(
                f"WebSocket connection denied: User {user} is not authenticated or not a member of project {self.project_id}"
            )
            await self.close(
                code=4003
            )  # Use a specific close code (4003 is often used for authentication/authorization failure)

    async def disconnect(self, close_code):
        """
        Handles WebSocket disconnection.
        Removes the user's channel from the project group.
        """
        print(f"WebSocket disconnected with code: {close_code}")
        # Leave the project group
        if self.channel_layer is not None:
            await self.channel_layer.group_discard(
                self.project_group_name, self.channel_name
            )

    async def receive(self, text_data):
        """
        Handles receiving messages from the WebSocket.
        (Optional: Can be used for client-to-server messages, e.g., user activity indicators)
        """
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get("type")
        user = self.scope["user"]

        if not user.is_authenticated:
            # Ignore messages from unauthenticated users (shouldn't happen if connect logic is correct)
            return

        print(
            f"Received message from {user.username} in group {self.project_group_name}: {message_type}"
        )

        # Handle different message types from the client
        if message_type == "user_activity":
            activity_content = text_data_json.get("content")
            task_id = text_data_json.get(
                "task_id"
            )  # Assuming activity is often task-specific
            await self.handle_user_activity(user, activity_content, task_id)

        # Add other client-to-server message handlers here if needed
        # elif message_type == 'mark_comments_read':
        #     task_id = text_data_json.get('task_id')
        #     await self.mark_comments_as_read(user, task_id)

    # --- Handlers for messages received from the Channel Layer Group ---
    # These methods are called when a message is sent to the project group
    # using channel_layer.group_send({'type': 'method_name', ...})

    async def task_created(self, event):
        """
        Handles messages indicating a new task was created in the project.
        Sends the new task data to connected clients.
        Expected event structure: {'type': 'task_created', 'task': serialized_task_data}
        """
        task_data = event["task"]
        payload = {"type": "task_created", "task": task_data}
        await self.send(text_data=json.dumps(payload, cls=DjangoJSONEncoder))
        print(f"Sent task_created message to group {self.project_group_name}")

    async def task_updated(self, event):
        """
        Handles messages indicating a task in the project was updated.
        Sends the updated task data to connected clients.
        Expected event structure: {'type': 'task_updated', 'task': serialized_task_data}
        """
        task_data = event["task"]
        payload = {"type": "task_updated", "task": task_data}
        await self.send(text_data=json.dumps(payload, cls=DjangoJSONEncoder))
        print(f"Sent task_updated message to group {self.project_group_name}")

    async def comment_added(self, event):
        """
        Handles messages indicating a new comment was added to a task in the project.
        Sends the new comment data to connected clients.
        Expected event structure: {'type': 'comment_added', 'comment': serialized_comment_data}
        """
        comment_data = event["comment"]
        payload = {"type": "comment_added", "comment": comment_data}
        await self.send(
            await self.send(text_data=json.dumps(payload, cls=DjangoJSONEncoder))
        )
        print(f"Sent comment_added message to group {self.project_group_name}")

    async def user_activity_message(self, event):
        """
        Handles user activity messages broadcast within the project group.
        Sends the activity data back to the WebSocket.
        Expected event structure: {'type': 'user_activity_message', 'user_id': ..., 'username': ..., 'activity': ..., 'task_id': ..., 'timestamp': ...}
        """
        # Send the activity data back to the WebSocket
        await self.send(
            text_data=json.dumps(
                {
                    "type": "user_activity",
                    "user_id": event["user_id"],
                    "username": event["username"],
                    "activity": event["activity"],
                    "task_id": event.get("task_id"),  # task_id might be optional
                    "timestamp": event["timestamp"],
                }
            )
        )
        print(
            f"Sent user activity '{event.get('activity')}' from {event.get('username')} to WebSocket in group {self.project_group_name}"
        )

    # --- Helper Methods (for handling client messages or database interaction) ---

    async def handle_user_activity(self, user, activity_content, task_id):
        """
        Processes user activity messages received from the client and broadcasts them.
        """
        # You might want to validate the activity_content or task_id here
        if activity_content in ["typing", "viewing"]:
            await self.channel_layer.group_send(
                self.project_group_name,
                {
                    "type": "user_activity_message",  # This calls the user_activity_message method
                    "user_id": str(user.id),
                    "username": user.username,
                    "activity": activity_content,
                    "task_id": str(task_id) if task_id else None,
                    "timestamp": timezone.now().isoformat(),
                },
            )

    @database_sync_to_async
    def is_project_member(self, user, project_id):
        """
        Checks if the given user is a member of the project with the given ID.
        Runs database query asynchronously.
        """
        if user.is_anonymous:
            return False
        try:
            project = Project.objects.get(id=project_id)
            return project.members.filter(id=user.id).exists()
        except Project.DoesNotExist:
            return False
