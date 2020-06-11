from django.contrib import admin
from .models import MapPoint


class MapPointAdmn(admin.ModelAdmin):
    list_display = [
        'id',
        'product',
        'lat',
        'long'
    ]


admin.site.register(MapPoint, MapPointAdmn)