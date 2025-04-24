from rest_framework import serializers
from apps.v1.comments.models import Comment


class CommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for Listing projects.
    """

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "seen_by")

    def create(self, validated_data):
        validated_data["author_id"] = self.context["user"].id
        validated_data["task_id"] = self.context["task_id"]
        print(validated_data)
        comment = Comment.objects.create(**validated_data)
        return comment


class CommentUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for Update comment
    """

    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at", "seen_by", "author", "task")
