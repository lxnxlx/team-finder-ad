from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


def index(request):
    return redirect("projects:list")


urlpatterns = [
    path("", index),
    path("admin/", admin.site.urls),
    path("projects/", include("projects.urls")),
    path("project/", include(("projects.urls", "project_legacy"), namespace="project_legacy")),
    path("users/", include("users.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
