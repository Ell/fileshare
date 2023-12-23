import os

from django.db import models
from django.db.models.functions import Now
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

from taggit.managers import TaggableManager
import shortuuid

from fileshare.thumbnail import create_image_thumbnail, create_video_thumbnail


def get_upload_path(instance, filename):
    _name, ext = os.path.splitext(filename)
    file_id = shortuuid.ShortUUID().random(length=8)

    return f"{file_id}{ext}"


class Upload(models.Model):
    class FileType(models.TextChoices):
        VIDEO = "VIDEO", _("Video")
        IMAGE = "IMAGE", _("Image")
        AUDIO = "AUDIO", _("Audio")
        TEXT = "TEXT", _("Text")
        OTHER = "OTHER", _("Other")

    class UploadVisibility(models.TextChoices):
        PUBLIC = "PUBLIC", _("Public")
        HIDDEN = "HIDDEN", _("Hidden")
        PRIVATE = "PRIVATE", _("Private")

    description = models.TextField(blank=True, default="")
    title = models.CharField(max_length=256, blank=True, default="")
    file = models.FileField(upload_to=get_upload_path)
    visibility = models.CharField(
        max_length=16,
        choices=UploadVisibility,
        default=UploadVisibility.HIDDEN,
    )
    posted_date = models.DateTimeField(auto_now_add=True, db_default=Now())
    tags = TaggableManager(blank=True)
    file_type = models.CharField(
        max_length=16, choices=FileType, default=FileType.OTHER, editable=False
    )
    thumbnail = models.FileField(
        upload_to="thumbnails/", blank=True, null=True, editable=False
    )

    def __str__(self):
        return f"{self.file.name}"


@receiver(pre_save, sender=Upload)
def _set_file_type_on_save(sender, instance, *args, **kwargs):
    if instance.pk:
        return

    _name, ext = os.path.splitext(instance.file.name)

    file_type = Upload.FileType.OTHER

    if ext in [".mp4", ".webm", ".ogv"]:
        file_type = Upload.FileType.VIDEO
    elif ext in [".mp3", ".ogg", ".wav"]:
        file_type = Upload.FileType.AUDIO
    elif ext in [".png", ".jpeg", ".jpg", ".gif", ".webp"]:
        file_type = Upload.FileType.IMAGE

    instance.file_type = file_type


@receiver(post_save, sender=Upload)
def _create_thumbnail_on_save(sender, instance, *args, **kwargs):
    if instance.thumbnail:
        return

    if instance.file_type == Upload.FileType.VIDEO:
        create_video_thumbnail(instance)

    if instance.file_type == Upload.FileType.IMAGE:
        create_image_thumbnail(instance)


class APIKey(models.Model):
    key = models.CharField(max_length=16, blank=True, null=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} - {self.key}"


@receiver(pre_save, sender=APIKey)
def _create_random_api_key(sender, instance, *args, **kwargs):
    instance.key = shortuuid.ShortUUID().random(length=16)
