"""
URL configuration for tickethub_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    # Auth
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # User
    path("api/v1/users/", include("apps.v1.userprofile.urls", namespace="userprofile")),
    # Project, Task, Comments
    path("api/v1/projects/", include("apps.v1.projects.urls", namespace="projects")),
    path("api/v1/projects/", include("apps.v1.tasks.urls", namespace="tasks")),
    path("api/v1/projects/", include("apps.v1.comments.urls", namespace="comments")),
    # App based API versioning used currently
    # But, We also have support for View level versioning, so you can use the same View for different versions of the API.
    # path('api/<str:version>/projects/', include('apps.v1.projects.urls', namespace='projects')),
    # path('api/<str:version>/projects/', include('apps.v1.projects.urls', namespace='projects')),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += [path("silk/", include("silk.urls", namespace="silk"))]
