from django.contrib import admin

from .models import Upload, APIKey


admin.site.register(Upload)
admin.site.register(APIKey)
