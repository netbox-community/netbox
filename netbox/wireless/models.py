from django.db import models

from extras.utils import extras_features
from netbox.models import PrimaryModel
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'SSID',
)


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class SSID(PrimaryModel):
    """
    A service set identifier belonging to a wireless network.
    """
    name = models.CharField(
        max_length=32
    )
    vlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='VLAN'
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ('name', 'pk')
        verbose_name = 'SSID'
        verbose_name_plural = 'SSIDs'

    def __str__(self):
        return self.name
