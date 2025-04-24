from django.db import models

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

from apps.common.models import BaseModel, CustomUser
from apps.v1.projects.models import Project
from django.utils import timezone


class TaskModelManager(models.Manager):
    def existing(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def delete(self, *args, **kwargs):
        return super().get_queryset().update(deleted_at=timezone.now())


# Create your models here.
class Task(BaseModel):
    """
    Represents a task within a project.
    """

    class TaskStatus(models.TextChoices):
        TODO = "TODO", "To Do"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        DONE = "DONE", "Done"

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    creator = models.ForeignKey(
        CustomUser, on_delete=models.SET_NULL, null=True, related_name="created_tasks"
    )
    assignee = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    title = models.CharField(max_length=255)
    description = MarkdownField(
        rendered_field="text_rendered",
        validator=VALIDATOR_STANDARD,
        blank=True,
        null=True,
    )
    description_rendered = RenderedMarkdownField()
    status = models.CharField(
        max_length=20, choices=TaskStatus.choices, default=TaskStatus.TODO
    )
    due_date = models.DateField(null=True, blank=True)

    objects = TaskModelManager()

    def __str__(self):
        return f"{self.title} ({self.project.title})"

    def soft_delete(self, save=True):
        self.deleted_at = timezone.now()
        if save:
            self.save(update_fields=["deleted_at"])
