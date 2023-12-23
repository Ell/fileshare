from io import BytesIO
import os

from django.conf import settings
from django.core.files.base import ContentFile

from PIL import Image
from celery import Celery
import ffmpeg


def create_image_thumbnail(upload):
    name, _ext = os.path.splitext(upload.file.name)

    upload_file_bytes = upload.file.read()

    thumbnail_buffer = BytesIO()

    thumbnail = Image.open(BytesIO(upload_file_bytes))
    thumbnail.thumbnail((250, 250))
    thumbnail.save(fp=thumbnail_buffer, format="PNG")

    thumbnail_file = ContentFile(thumbnail_buffer.getvalue())

    thumbnail_file_name = f"{name}_thumbnail.png"

    upload.thumbnail.save(thumbnail_file_name, thumbnail_file, save=True)


def create_video_thumbnail(upload):
    file_url = upload.file.url
    probe = ffmpeg.probe(file_url)
    stream = probe["streams"][0]

    duration = stream.get("duration")

    if duration:
        time = duration // 2
    else:
        time = 0

    width = probe["streams"][0]["width"]

    image_bytes = (
        ffmpeg.input(file_url, ss=time)
        .filter("scale", width, -1)
        .output("pipe:", format="apng", vframes=1, loglevel="quiet")
        .run(capture_stdout=True)
    )

    thumbnail_buffer = BytesIO()

    thumbnail = Image.open(BytesIO(image_bytes[0]))
    thumbnail.thumbnail((250, 250))
    thumbnail.save(fp=thumbnail_buffer, format="PNG")

    thumbnail_file = ContentFile(thumbnail_buffer.getvalue())

    name, _ext = os.path.splitext(upload.file.name)
    thumbnail_file_name = f"{name}_thumbnail.png"

    upload.thumbnail.save(thumbnail_file_name, thumbnail_file, save=True)
