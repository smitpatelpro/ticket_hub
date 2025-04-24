from django.urls import path
from . import views

app_name = "userprofile"

urlpatterns = [
    path("", views.UserCreateView.as_view(), name="user_create"),
    path("me/", views.UserProfileView.as_view(), name="me"),
    path("me/picture/", views.UserProfilePicutreView.as_view(), name="me_picture"),
]
