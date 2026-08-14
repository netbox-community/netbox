from django.db import models

from netbox.models import NetBoxModel
from utilities.querysets import RestrictedQuerySet


class DummyModel(models.Model):
    name = models.CharField(
        max_length=20
    )
    number = models.IntegerField(
        default=100
    )

    class Meta:
        ordering = ['name']


class DummySiteAttachment(models.Model):
    site = models.ForeignKey(
        to='dcim.Site',
        on_delete=models.CASCADE,
        related_name='dummy_site_attachments'
    )
    name = models.CharField(
        max_length=20
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ['name']


class DummyNetBoxModel(NetBoxModel):
    pass
