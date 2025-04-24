from django.urls import path
from . import views

app_name = "tasks"

urlpatterns = [
    path('<uuid:project_id>/tasks/', views.TasksListView.as_view(), name='tasks_list'),
    path('<uuid:project_id>/tasks/<uuid:task_id>/', views.TasksDetailView.as_view(), name='tasks_details'),
]

