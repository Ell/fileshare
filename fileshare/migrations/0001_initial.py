# Generated by Django 5.0 on 2023-12-22 17:32

import django.db.models.deletion
import django.db.models.functions.datetime
import fileshare.models
import taggit.managers
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        (
            "taggit",
            "0006_rename_taggeditem_content_type_object_id_taggit_tagg_content_8fc721_idx",
        ),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="APIKey",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("key", models.CharField(max_length=16)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Upload",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("description", models.TextField(blank=True, default="")),
                ("title", models.CharField(blank=True, default="", max_length=256)),
                ("file", models.FileField(upload_to=fileshare.models.get_upload_path)),
                (
                    "visibility",
                    models.CharField(
                        choices=[
                            ("PUBLIC", "Public"),
                            ("HIDDEN", "Hidden"),
                            ("PRIVATE", "Private"),
                        ],
                        default="Hidden",
                        max_length=32,
                    ),
                ),
                (
                    "posted_date",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_default=django.db.models.functions.datetime.Now(),
                    ),
                ),
                (
                    "thumbnail",
                    models.FileField(blank=True, null=True, upload_to="thumbnails/"),
                ),
                (
                    "tags",
                    taggit.managers.TaggableManager(
                        blank=True,
                        help_text="A comma-separated list of tags.",
                        through="taggit.TaggedItem",
                        to="taggit.Tag",
                        verbose_name="Tags",
                    ),
                ),
            ],
        ),
    ]
