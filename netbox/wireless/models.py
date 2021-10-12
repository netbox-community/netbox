from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from dcim.constants import WIRELESS_IFACE_TYPES
from extras.utils import extras_features
from netbox.models import BigIDModel, PrimaryModel
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'WirelessLAN',
)


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class WirelessLAN(PrimaryModel):
    """
    A service set identifier belonging to a wireless network.
    """
    ssid = models.CharField(
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
        ordering = ('ssid', 'pk')
        verbose_name = 'Wireless LAN'

    def __str__(self):
        return self.ssid

    def get_absolute_url(self):
        return reverse('wireless:ssid', args=[self.pk])
