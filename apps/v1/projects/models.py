from django.db import models
from django.utils import timezone
from apps.common.models import BaseModel
from apps.common.models import CustomUser


# Create your models here.
class Project(BaseModel):
    """
    Represents a project within the platform.
    """

    title = models.CharField(max_length=255)
    members = models.ManyToManyField(
        CustomUser, through="ProjectMembership", related_name="projects"
    )

    def __str__(self):
        return self.title


class ProjectMembership(BaseModel):
    """
    Represents an active membership of a User in a Project.
    """

    class ProjectRole(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        MEMBER = "MEMBER", "Member"

    class MembershipStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="memberships"
    )
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="memberships"
    )
    date_joined = models.DateTimeField(
        auto_now_add=True
    )  # Timestamp of when the membership became active

    # Status of the membership within the project
    status = models.CharField(
        max_length=20, choices=MembershipStatus.choices, default=MembershipStatus.ACTIVE
    )

    role = models.CharField(
        max_length=20, choices=ProjectRole.choices, default=ProjectRole.MEMBER
    )

    class Meta:
        unique_together = (
            "user",
            "project",
        )  # Ensures a user can only have one active membership per project

    def __str__(self):
        return f"{self.user.username} is {self.status} in {self.project.title}"


class ProjectInvitation(BaseModel):
    """
    Represents an invitation for a User to join a Project.
    """

    class InvitationStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"
        CANCELLED = "CANCELLED", "Cancelled"

    # The user who is being invited.
    # Note: This could be a ForeignKey to User if the user must exist to be invited,
    # or you might store an email if inviting users who don't yet have an account.
    # For simplicity here, assuming inviting existing users.
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="project_invitations"
    )
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="invitations"
    )
    role = models.CharField(
        max_length=20,
        choices=ProjectMembership.ProjectRole.choices,
        default=ProjectMembership.ProjectRole.MEMBER,
    )
    invited_by = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="sent_invitations"
    )  # Who sent the invitation

    invitation_status = models.CharField(
        max_length=20,
        choices=InvitationStatus.choices,
        default=InvitationStatus.PENDING,
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(
        null=True, blank=True
    )  # Timestamp when the user accepted or rejected

    class Meta:
        # A user can have only one PENDING invitation for a given project at a time
        unique_together = (
            "user",
            "project",
            "invitation_status",
        )  # Consider this constraint carefully based on exact requirements

    def __str__(self):
        return f"Invitation for {self.user.username} to join {self.project.title} (Status: {self.invitation_status})"

    def accept(self):
        if self.invitation_status == self.InvitationStatus.PENDING:
            # Create the active membership
            ProjectMembership.objects.create(user=self.user, project=self.project)
            self.invitation_status = self.InvitationStatus.ACCEPTED
            self.responded_at = timezone.now()
            self.save()

    def reject(self):
        if self.invitation_status == self.InvitationStatus.PENDING:
            self.invitation_status = self.InvitationStatus.REJECTED
            self.responded_at = timezone.now()
            self.save()

    def cancel(self):
        if self.invitation_status == self.InvitationStatus.PENDING:
            self.invitation_status = self.InvitationStatus.CANCELLED
            self.responded_at = timezone.now()  # Or a separate cancelled_at field
            self.save()
