from django.db import models
from apps.common.models import BaseModel, CustomUser
from apps.v1.tasks.models import Task



class Comment(BaseModel):
    """
    Represents a comment on a task.
    """

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="comments"
    )
    content = models.TextField()

    class Meta:
        ordering = ["created_at"]  # Order comments chronologically

    def __str__(self):
        return f"Comment by {self.author.username} on Task {self.task.title}"
