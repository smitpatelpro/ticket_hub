from django.db import models
from markdownfield.models import MarkdownField, RenderedMarkdownField
from markdownfield.validators import VALIDATOR_STANDARD
from apps.common.models import BaseModel, CustomUser
from apps.v1.tasks.models import Task
from django.utils import timezone


class CommentModelManager(models.Manager):
    def existing(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def delete(self, *args, **kwargs):
        return super().get_queryset().update(deleted_at=timezone.now())


class Comment(BaseModel):
    """
    Represents a comment on a task.
    """

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments"
    )
    content = MarkdownField(
        rendered_field="text_rendered",
        validator=VALIDATOR_STANDARD,
        blank=True,
        null=True,
    )
    content_rendered = RenderedMarkdownField()

    seen_by = models.ManyToManyField(
        CustomUser, related_name="comments_seen", null=True, blank=True
    )

    objects = CommentModelManager()

    class Meta:
        ordering = ["created_at"]  # Order comments chronologically

    def __str__(self):
        return f"Comment by {self.author.username} on Task {self.task.title}"

    def soft_delete(self, save=True):
        self.deleted_at = timezone.now()
        if save:
            self.save(update_fields=["deleted_at"])
