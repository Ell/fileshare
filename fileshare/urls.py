from django.contrib import admin
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.FileListView.as_view(), name="index"),
    path("tag/<str:tag_name>", views.TagListView.as_view(), name="tag_view"),
    path("<str:file_name>", views.file_view, name="file_view"),
    path("files/upload", views.upload_file, name="upload_view"),
    path("__reload__/", include("django_browser_reload.urls")),
    path("admin/", admin.site.urls),
]
