from django.urls import path
from . import views

app_name = "projects"

urlpatterns = [
    # Define your app-specific URL patterns here
    path('', views.HelloView.as_view(), name='hello'),
    # Add more paths as needed
]

