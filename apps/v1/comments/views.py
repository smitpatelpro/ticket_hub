from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, mixins, response, exceptions

from apps.common.constants import TASK_NOT_FOUND, PERMISSION_DENIED
from apps.v1.comments.serializers import (
    CommentCreateSerializer,
    CommentUpdateSerializer,
)
from apps.v1.tasks.models import Task
from django.utils import timezone
from apps.v1.comments.models import Comment
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()


class CommentListView(
    generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """
    API view to list all projects.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CommentCreateSerializer
    queryset = Comment.objects.all()

    def get_serializer_context(self):
        """
        Override this method to pass custom context to the serializer.
        In this case, we pass the requesting user.
        """
        context = (
            super().get_serializer_context()
        )  # Get the default context (request, view, format)

        task_id = self.kwargs.get("task_id")
        context["user"] = self.request.user  # Add the requesting user to the context
        context["task_id"] = task_id
        return context

    def get(self, request, project_id, task_id, *args, **kwargs):
        """
        Handles GET requests to list all projects.
        """
        valid_task = (
            Task.objects.existing().filter(id=task_id, project_id=project_id).exists()
        )
        if not valid_task:
            raise exceptions.NotFound(TASK_NOT_FOUND)

        self.queryset = self.queryset.filter(task_id=task_id)
        return self.list(request, *args, **kwargs)

    def post(self, request, project_id, task_id, *args, **kwargs):
        """
        Handles POST requests to create a new project.
        """
        request.data["author"] = request.user.id
        request.data["task"] = task_id
        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        project_id = self.kwargs.get("project_id")
        comment = serializer.save()
        serializer = CommentCreateSerializer(comment)
        async_to_sync(channel_layer.group_send)(
            f"project_{project_id}",
            {
                "type": "task_created",  # This matches the consumer method name
                "task": serializer.data,  # The data to send to the consumer
            },
        )


class CommentDetailView(
    generics.GenericAPIView, mixins.RetrieveModelMixin, mixins.UpdateModelMixin
):
    """
    API view to list all projects.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CommentUpdateSerializer
    queryset = Comment.objects.existing()

    def get_object(self):
        project_id = self.kwargs.get("project_id")
        task_id = self.kwargs.get("task_id")
        comment_id = self.kwargs.get("comment_id")

        valid_task = (
            Task.objects.existing().filter(id=task_id, project_id=project_id).exists()
        )
        if not valid_task:
            raise exceptions.NotFound(TASK_NOT_FOUND)

        try:
            comment = self.queryset.get(id=comment_id, task_id=task_id)
        except Task.DoesNotExist:
            raise exceptions.NotFound(
                "comment does not exist for given task and project"
            )
        return comment

    def get(self, request, project_id, task_id, *args, **kwargs):
        """
        Handles GET requests to list all projects.
        """
        return self.retrieve(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new project.
        """
        project_id = self.kwargs.get("project_id")
        task_id = self.kwargs.get("task_id")
        comment_id = self.kwargs.get("comment_id")
        valid_task = (
            Task.objects.existing().filter(id=task_id, project_id=project_id).exists()
        )
        if not valid_task:
            raise exceptions.NotFound(TASK_NOT_FOUND)

        comment = (
            self.queryset.filter(id=comment_id, task_id=task_id).only("author").first()
        )
        if comment and comment.author != request.user:
            raise exceptions.PermissionDenied(PERMISSION_DENIED)

        if timezone.now() >= comment.created_at + timezone.timedelta(minutes=5):
            raise exceptions.PermissionDenied(
                PERMISSION_DENIED + " after 5 minutes of creation."
            )
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new project.
        """
        task_id = self.kwargs.get("task_id")
        project_id = self.kwargs.get("project_id")
        comment_id = self.kwargs.get("comment_id")

        valid_task = (
            Task.objects.existing().filter(id=task_id, project_id=project_id).exists()
        )
        if not valid_task:
            raise exceptions.NotFound(TASK_NOT_FOUND)

        comment_qs = self.queryset.filter(
            id=comment_id, task_id=task_id
        ).only("author")

        comment = comment_qs.first()
        if comment and comment.author != request.user:
            raise exceptions.PermissionDenied(
                "You are not allowed to update this task."
            )

        if not comment:
            raise exceptions.NotFound(TASK_NOT_FOUND)

        if timezone.now() >= comment.created_at + timezone.timedelta(minutes=5):
            raise exceptions.PermissionDenied(
                "You are not allowed to update this task after 5 minutes."
            )

        # Soft delete
        comment.soft_delete()
        return response.Response(status=204)


class CommentReadView(
    generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """
    API view to list all projects.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = CommentCreateSerializer
    queryset = Comment.objects.all()

    def post(self, request, project_id, task_id, *args, **kwargs):
        """
        Handles POST requests to create a new project.
        """
        request.data["author"] = request.user.id
        request.data["task"] = task_id
        return self.create(request, *args, **kwargs)
