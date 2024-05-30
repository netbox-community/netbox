from django.db import models

from netbox.models import EventRulesMixin, ChangeLoggingMixin

class DummyModel(EventRulesMixin, ChangeLoggingMixin, models.Model):
    name = models.CharField(
        max_length=20
    )
    number = models.IntegerField(
        default=100
    )
    serializer_label = 'netbox.tests.dummy_plugin'

    class Meta:
        ordering = ['name']
