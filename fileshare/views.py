import os
from typing import Any
from django.db.models.query import QuerySet

from django.http import HttpResponse, HttpResponseNotFound
from django.core.exceptions import BadRequest
from django.views.decorators.csrf import csrf_exempt
from django.template import loader
from django.urls import reverse
from django.views.generic.list import ListView

from .models import APIKey, Upload
from .forms import UploadForm


class TagListView(ListView):
    model = Upload
    paginate_by = 12
    context_object_name = "upload_list"
    template_name = "file_list.html"

    def get_queryset(self):
        return Upload.objects.filter(tags__name__in=[self.kwargs["tag_name"]]).order_by(
            "-pk"
        )


class FileListView(ListView):
    model = Upload
    paginate_by = 12
    context_object_name = "upload_list"
    queryset = Upload.objects.filter(
        visibility=Upload.UploadVisibility.PUBLIC
    ).order_by("-pk")
    template_name = "file_list.html"


def file_view(request, file_name):
    try:
        upload = Upload.objects.get(file=file_name)
    except Upload.DoesNotExist:
        return HttpResponseNotFound("File not found")

    if upload.visibility == "PRIVATE" and not request.user.is_authenticated:
        return HttpResponseNotFound("File not found")

    tags = upload.tags.all()

    context = {"upload": upload, "tags": tags}
    template = loader.get_template("file.html")

    return HttpResponse(template.render(context, request))


@csrf_exempt
def upload_file(request):
    if request.method != "POST":
        raise BadRequest("Invalid request")

    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise BadRequest("Missing Authorization Token")

    token = auth_header.replace("Bearer ", "")
    try:
        APIKey.objects.get(key=token)
    except APIKey.DoesNotExist:
        raise BadRequest("Invalid token provided")

    form = UploadForm(request.POST, request.FILES)
    if form.is_valid():
        upload = form.save()

        url_path = reverse("file_view", args=[upload.file.name])

        return HttpResponse(f"https://i.ell.dev{url_path}")
