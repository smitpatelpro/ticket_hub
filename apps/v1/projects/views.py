from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, mixins, response, exceptions

from apps.common.constants import PERMISSION_DENIED
from apps.v1.projects.models import Project, ProjectInvitation, ProjectMembership
from apps.v1.projects.serializers import (
    ProjectFullSerializer,
    ProjectInvitationSerializer,
    ProjectMembershipSerializer,
    ProjectSerializer,
)


class ProjectListView(
    generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """
    API view to list all projects.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectSerializer
    queryset = Project.objects.existing()

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

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to list all projects.
        """
        full_data = request.query_params.get("full_data", None)
        full_data = True if full_data == "true" else False
        if full_data:
            self.serializer_class = ProjectFullSerializer
        else:
            self.serializer_class = ProjectSerializer
        # Filter projects by the authenticated user
        self.queryset = self.queryset.filter(members=request.user)

        # Filter projects by status if provided in the query parameters
        project_status = request.query_params.get("status", None)
        if project_status:
            self.queryset = self.queryset.filter(status=project_status)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new project.
        """

        return self.create(request, *args, **kwargs)

    def perform_create(self, serializer):
        proj = serializer.save()
        ProjectMembership.objects.create(
            user=self.request.user,
            project=proj,
            role=ProjectMembership.ProjectRole.OWNER,
        )
        # Example: Send a welcome email
        # send_welcome_email(proj)


class InviteProjectMemberListView(
    generics.GenericAPIView, mixins.ListModelMixin, mixins.CreateModelMixin
):
    """
    API view to list all projects.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectInvitationSerializer
    queryset = ProjectInvitation.objects.all()

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

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests to list all projects.
        """
        invite_type = request.query_params.get("invite_type", None)
        if invite_type not in ["sent", "received"]:
            raise exceptions.ValidationError(
                {"invite_type": ["Invalid value. Must be 'sent' or 'received'."]}
            )

        if invite_type == "sent":
            # Filter invites sent by the authenticated user
            self.queryset = self.queryset.filter(invited_by=request.user)
        elif invite_type == "received":
            # Filter invites received by the authenticated user
            self.queryset = self.queryset.filter(user=request.user)

        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests to create a new project.
        """
        # Check if the user is already member of the project
        existing_membership_qs = ProjectMembership.objects.filter(
            user_id=request.data["user"],
            project_id=request.data["project"],
            status=ProjectMembership.MembershipStatus.ACTIVE,
        )
        if existing_membership_qs.exists():
            raise exceptions.ValidationError(
                {"error": ["User is already a member of this project."]}
            )

        # Check if the user is already invited to the project
        existing_invite_qs = ProjectInvitation.objects.filter(
            user_id=request.data["user"],
            project_id=request.data["project"],
            invitation_status=ProjectInvitation.InvitationStatus.PENDING,
        )
        if existing_invite_qs.exists():
            return response.Response(
                {"error": "User is already a invited to this project."}, status=400
            )

        # Only Admin can invite as Admin
        if (
            "role" in request.data
            and request.data["role"] == ProjectMembership.ProjectRole.ADMIN
        ):
            membership: ProjectMembership = (
                request.user.memberships.filter(
                    project__id=request.data["project"],
                    status=ProjectMembership.MembershipStatus.ACTIVE,
                )
                .only("role", "user_id")
                .first()
            )
            if membership:
                if membership.role == ProjectMembership.ProjectRole.ADMIN:
                    request.data["role"] = request.data["role"]
                else:
                    raise exceptions.PermissionDenied(
                        PERMISSION_DENIED + ". Consider inviting as member"
                    )

        return self.create(request, *args, **kwargs)


class InviteActionView(generics.GenericAPIView, mixins.CreateModelMixin):
    """
    API view to list all projects.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ProjectInvitationSerializer
    queryset = ProjectInvitation.objects.all()

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

    def post(self, request, invite_id, action, *args, **kwargs):
        """
        Handles POST requests to create a new project.
        """

        if action not in ["accept", "reject", "cancel"]:
            raise exceptions.ValidationError(
                {"action": ["Invalid value. Must be one of accept, reject or cancel."]}
            )
            # return response.Response({"error": "Invalid action."}, status=400)

        # Check if invite is valid and authorized
        invite: ProjectInvitation = ProjectInvitation.objects.filter(
            id=invite_id,
            # user=request.user,
            invitation_status=ProjectInvitation.InvitationStatus.PENDING,
        ).last()

        if not invite:
            return response.Response({"error": "Invite does not exist."}, status=400)

        if action == "accept":
            existing_membership = ProjectMembership.objects.filter(
                user=invite.user, project=invite.project
            ).first()
            if existing_membership:
                return response.Response(
                    {"error": "User is already a member of this project."}, status=400
                )

            if request.user != invite.user:
                raise exceptions.PermissionDenied(PERMISSION_DENIED)
            membership = invite.accept()
            data = ProjectMembershipSerializer(membership).data
            return response.Response(data, status=200)

        elif action == "reject":
            if request.user != invite.user:
                raise exceptions.PermissionDenied(PERMISSION_DENIED)
            invite.reject()
            invite: ProjectInvitation = ProjectInvitation.objects.get(id=invite_id)
            serializer = ProjectInvitationSerializer(invite)
            return response.Response(serializer.data, status=200)

        elif action == "cancel":
            if request.user != invite.invited_by:
                raise exceptions.PermissionDenied(PERMISSION_DENIED)
            invite.cancel()
            invite: ProjectInvitation = ProjectInvitation.objects.get(id=invite_id)
            serializer = ProjectInvitationSerializer(invite)
            return response.Response(serializer.data, status=200)
