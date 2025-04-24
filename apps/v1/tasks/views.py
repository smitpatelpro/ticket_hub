from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, mixins, response, exceptions

from apps.common.constants import TASK_NOT_FOUND
from apps.v1.tasks.models import Task
from apps.v1.tasks.serializers import TaskSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()


class TasksListView(
    generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """
    API view to list all projects.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    queryset = Task.objects.all()

    def get_serializer_context(self):
        """
        Override this method to pass custom context to the serializer.
        In this case, we pass the requesting user.
        """
        context = (
            super().get_serializer_context()
        )  # Get the default context (request, view, format)
        context["user"] = self.request.user  # Add the requesting user to the context
        return context

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        return self.queryset.filter(project_id=project_id)

    def get(self, request, project_id, *args, **kwargs):
        """
        Handles GET requests to list all projects.
        """
        # self.queryset = self.queryset.filter(project_id=project_id)

        return self.list(request, *args, **kwargs)

    def post(self, request, project_id, *args, **kwargs):
        """
        Handles POST requests to create a new project.
        """
        response = self.create(request, *args, **kwargs)

        return response

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_id")
        task = serializer.save()
        serializer = TaskSerializer(task)
        async_to_sync(channel_layer.group_send)(
            f"project_{project_id}",
            {
                "type": "task_created",  # This matches the consumer method name
                "task": serializer.data,  # The data to send to the consumer
            },
        )


class TasksDetailView(
    generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API view to list all projects.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = TaskSerializer
    queryset = Task.objects.existing()

    def get_object(self):
        task_id = self.kwargs.get("task_id")
        project_id = self.kwargs.get("project_id")
        try:
            task = self.queryset.get(id=task_id, project_id=project_id)
        except Task.DoesNotExist:
            raise exceptions.NotFound(TASK_NOT_FOUND)
        return task

    def get(self, request, project_id, task_id, *args, **kwargs):
        """
        Handles GET requests to list all projects.
        """
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new project.
        """
        task_id = self.kwargs.get("task_id")
        project_id = self.kwargs.get("project_id")
        task = (
            self.queryset.filter(id=task_id, project_id=project_id)
            .only("creator", "assignee")
            .first()
        )
        if task and task.creator != request.user and task.assignee != request.user:
            raise exceptions.PermissionDenied(
                "You are not allowed to update this task."
            )

        return self.partial_update(request, *args, **kwargs)

    def perform_update(self, serializer):
        project_id = self.kwargs.get("project_id")
        task = serializer.save()
        serializer = TaskSerializer(task)
        async_to_sync(channel_layer.group_send)(
            f"project_{project_id}", {"type": "task_updated", "task": serializer.data}
        )

    def delete(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new project.
        """
        task_id = self.kwargs.get("task_id")
        project_id = self.kwargs.get("project_id")
        task_qs = self.queryset.filter(id=task_id, project_id=project_id).only(
            "creator", "assignee"
        )

        task = task_qs.first()
        if task and task.creator != request.user and task.assignee != request.user:
            raise exceptions.PermissionDenied(
                "You are not allowed to update this task."
            )

        if not task:
            raise exceptions.NotFound(TASK_NOT_FOUND)

        # Soft delete
        task.soft_delete()
        return response.Response(status=204)
