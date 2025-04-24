from django.db import models

from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD

from apps.common.models import BaseModel, CustomUser
from apps.v1.projects.models import Project


# Create your models here.
class Task(BaseModel):
    """
    Represents a task within a project.
    """

    class TaskStatus(models.TextChoices):
        TODO = "TODO", "To Do"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        DONE = "DONE", "Done"

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="tasks"
    )
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
    # description = models.TextField(blank=True, null=True)
    description = MarkdownField(rendered_field='text_rendered', validator=VALIDATOR_STANDARD, blank=True, null=True)
    description_rendered = RenderedMarkdownField()
    status = models.CharField(
        max_length=20, choices=TaskStatus.choices, default=TaskStatus.TODO
    )
    due_date = models.DateField(null=True, blank=True)
    # completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.project.title})"
