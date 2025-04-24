from django.contrib import admin

from apps.v1.comments.models import Comment

from .models import Task


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
