from __future__ import unicode_literals

import json

from django.core.serializers import serialize
from django.db import models

from extras.models import ObjectChange


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

        # Serialize the object using Django's built-in JSON serializer, then extract only the `fields` dict.
        json_str = serialize('json', [self])
        object_data = json.loads(json_str)[0]['fields']

        ObjectChange(
            user=user,
            request_id=request_id,
            changed_object=self,
            action=action,
            object_data=object_data
        ).save()
