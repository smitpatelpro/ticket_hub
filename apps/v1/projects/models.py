from django.db import models
from django.utils import timezone
from apps.common.models import BaseModel
from apps.common.models import CustomUser


# ========================================
# Model Managers
# ========================================
class ProjectManager(models.Manager):
    def active(self):
        return super().get_queryset().filter(status=Project.ProjectStatus.ACTIVE)

    def existing(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


# ========================================
# Models
# ========================================
class Project(BaseModel):
    """
    Represents a project within the platform.
    """

    class ProjectStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        ARCHIVED = "ARCHIVED", "Archived"

    title = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=20, choices=ProjectStatus.choices, default=ProjectStatus.ACTIVE
    )
    members = models.ManyToManyField(
        CustomUser, through="ProjectMembership", related_name="projects"
    )

    objects = ProjectManager()  # Custom manager to filter active projects

    def __str__(self):
        return self.title

    def soft_delete(self, save=True):
        self.deleted_at = timezone.now()
        if save:
            self.save(update_fields=["deleted_at"])

class ProjectMembership(BaseModel):
    """
    Represents an active membership of a User in a Project.
    """

    class ProjectRole(models.TextChoices):
        OWNER = "OWNER", "OWNER"
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

    # Note: This could be a ForeignKey to User if the user must exist to be invited,
    # or you might store an email if inviting users who don't yet have an account.
    # For simplicity here, we are assuming inviting users with existing account.
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
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="sent_invitations",
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

    # class Meta:
    #     unique_together = ()

    def __str__(self):
        return f"Invitation for {self.user.username} to join {self.project.title} (Status: {self.invitation_status})"

    def accept(self):
        if self.invitation_status == self.InvitationStatus.PENDING:
            # Create the active membership
            membership = ProjectMembership.objects.create(
                user=self.user,
                project=self.project,
                date_joined=timezone.now(),
                status=ProjectMembership.MembershipStatus.ACTIVE,
                role=self.role,
            )
            self.invitation_status = self.InvitationStatus.ACCEPTED
            self.responded_at = timezone.now()
            self.save(update_fields=["invitation_status", "responded_at"])
            return membership

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
