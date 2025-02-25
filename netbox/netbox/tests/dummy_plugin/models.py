from django.db import models

from netbox.models import NetBoxModel


class DummyModel(models.Model):
    name = models.CharField(
        max_length=20
    )
    number = models.IntegerField(
        default=100
    )

    class Meta:
        ordering = ['name']


class DummyNetBoxModel(NetBoxModel):
    pass
