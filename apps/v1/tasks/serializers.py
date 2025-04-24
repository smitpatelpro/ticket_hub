from rest_framework import serializers

from apps.v1.comments.serializers import CommentUpdateSerializer
from apps.v1.tasks.models import Task


class TaskSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for Listing tasks.
    """
    comments = CommentUpdateSerializer(many=True, read_only=True)
    unread_comments = serializers.SerializerMethodField()

    def get_unread_comments(self, obj):
        user = self.context.get("user")
        return obj.comments.exclude(seen_by=user).count()

    class Meta:
        model = Task
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "creator")
