from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    path("", views.ProjectListView.as_view(), name="project_list"),
    path("invite/", views.InviteProjectMemberListView.as_view(), name="invite_member"),
    path(
        "invite/<uuid:invite_id>/action/<str:action>/",
        views.InviteActionView.as_view(),
        name="invite_member_action",
    ),
]
