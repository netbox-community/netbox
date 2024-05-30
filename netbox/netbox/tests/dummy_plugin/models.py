from django.db import models


class DummyModel(models.Model):
    name = models.CharField(
        max_length=20
    )
    number = models.IntegerField(
        default=100
    )
    serializer_label = 'netbox.tests.dummy_plugin'

    class Meta:
        ordering = ['name']
