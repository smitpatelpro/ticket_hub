from django.urls import path
from . import views

app_name = "comments"

urlpatterns = [
    path(
        "<uuid:project_id>/tasks/<uuid:task_id>/comments/",
        views.CommentListView.as_view(),
        name="comment_list",
    ),
    path(
        "<uuid:project_id>/tasks/<uuid:task_id>/comments/<uuid:comment_id>/",
        views.CommentDetailView.as_view(),
        name="comment_detail",
    ),
]
