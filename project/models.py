from django.db import models


class MapPoint(models.Model):
    id = models.BigAutoField(primary_key=True)
    product = models.CharField(max_length=288, null=False, blank=False)
    lat = models.FloatField(null=False, blank=False)
    long = models.FloatField(null=False, blank=False)


