from __future__ import unicode_literals

from django.db import models

from extras.models import ObjectChange
from utilities.utils import serialize_object


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

    def log_change(self, user, request_id, action):
        """
        Create a new ObjectChange representing a change made to this object. This will typically be called automatically
        by extras.middleware.ChangeLoggingMiddleware.
        """
        ObjectChange(
            user=user,
            request_id=request_id,
            changed_object=self,
            action=action,
            object_data=serialize_object(self)
        ).save()
