from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    email = models.EmailField(_("email address"), unique=True)
    profile_picture = models.ImageField(
        _("profile picture"), upload_to="profile_pictures/", blank=True, null=True
    )
