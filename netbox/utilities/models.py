from __future__ import unicode_literals

from django.db import models


class ChangeLoggedModel(models.Model):
    """
    An abstract model which adds fields to store the creation and last-updated times for an object. Both fields can be
    null to facilitate adding these fields to existing instances via a database migration.
    """
    created = models.DateField(
        auto_now_add=True,
        blank=True,
        null=True
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        blank=True,
        null=True
    )

    class Meta:
        abstract = True
