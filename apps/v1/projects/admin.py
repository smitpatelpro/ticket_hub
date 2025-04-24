from django.contrib import admin
from .models import Project, ProjectMembership, ProjectInvitation


class ProjectMembershipInline(admin.TabularInline):
    model = ProjectMembership
    extra = 1


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectMembershipInline]


admin.site.register(ProjectMembership)
admin.site.register(ProjectInvitation)
