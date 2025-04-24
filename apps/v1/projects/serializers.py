from rest_framework import serializers
from apps.common.models import CustomUser
from apps.v1.projects.models import Project, ProjectInvitation, ProjectMembership
from django.db.models import Prefetch


class ProjectSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for Listing projects.
    """

    no_of_tasks_having_unread_comments = serializers.SerializerMethodField()

    def get_no_of_tasks_having_unread_comments(self, obj):
        return obj.tasks.exclude(comments__seen_by=self.context.get("user")).count()

    class Meta:
        model = Project
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "profile_picture",
            "is_active",
        )


class ProjectMembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = ProjectMembership
        fields = "__all__"

    @classmethod
    def eager_load(cls, queryset):
        """
        prefetch data from DB to avoid N+1 queries.
        """
        queryset = queryset.select_related("user")
        return queryset


class ProjectFullSerializer(serializers.ModelSerializer):
    """
    Serializer specifically for full project details.
    """

    memberships = ProjectMembershipSerializer(many=True)

    class Meta:
        model = Project
        fields = "__all__"

    @classmethod
    def eager_load(cls, queryset):
        """
        prefetch data from DB to avoid N+1 queries.
        """
        queryset = queryset.prefetch_related(
            Prefetch("memberships", queryset=ProjectMembership.objects.all()),
            Prefetch(
                "memberships__user",
                queryset=CustomUser.objects.only(UserSerializer.Meta.fields),
            ),
        )
        return queryset


class ProjectInvitationSerializer(serializers.ModelSerializer):
    """
    Serializer for ProjectInvitation model.
    """

    class Meta:
        model = ProjectInvitation
        fields = "__all__"

    def create(self, validated_data):
        user = self.context["user"]
        validated_data["invited_by"] = user
        return ProjectInvitation.objects.create(**validated_data)