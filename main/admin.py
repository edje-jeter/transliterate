from django.contrib import admin
from main.models import DictCMU


class DictCMUAdmin(admin.ModelAdmin):
    list_display = ('entry', 'list_length')

admin.site.register(DictCMU, DictCMUAdmin)
