from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey

from dcim.choices import LinkStatusChoices
from dcim.constants import WIRELESS_IFACE_TYPES
from extras.utils import extras_features
from netbox.models import BigIDModel, NestedGroupModel, PrimaryModel
from utilities.querysets import RestrictedQuerySet
from .choices import *
from .constants import *

__all__ = (
    'WirelessLAN',
    'WirelessLANGroup',
    'WirelessLink',
)


class WirelessAuthenticationBase(models.Model):
    """
    Abstract model for attaching attributes related to wireless authentication.
    """
    auth_type = models.CharField(
        max_length=50,
        choices=WirelessAuthTypeChoices,
        blank=True
    )
    auth_cipher = models.CharField(
        max_length=50,
        choices=WirelessAuthCipherChoices,
        blank=True
    )
    auth_psk = models.CharField(
        max_length=PSK_MAX_LENGTH,
        blank=True,
        verbose_name='Pre-shared key'
    )

    class Meta:
        abstract = True


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class WirelessLANGroup(NestedGroupModel):
    """
    A nested grouping of WirelessLANs
    """
    name = models.CharField(
        max_length=100,
        unique=True
    )
    slug = models.SlugField(
        max_length=100,
        unique=True
    )
    parent = TreeForeignKey(
        to='self',
        on_delete=models.CASCADE,
        related_name='children',
        blank=True,
        null=True,
        db_index=True
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    class Meta:
        ordering = ('name', 'pk')
        unique_together = (
            ('parent', 'name')
        )

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('wireless:wirelesslangroup', args=[self.pk])


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class WirelessLAN(WirelessAuthenticationBase, PrimaryModel):
    """
    A wireless network formed among an arbitrary number of access point and clients.
    """
    ssid = models.CharField(
        max_length=SSID_MAX_LENGTH,
        verbose_name='SSID'
    )
    group = models.ForeignKey(
        to='wireless.WirelessLANGroup',
        on_delete=models.SET_NULL,
        related_name='wireless_lans',
        blank=True,
        null=True
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
        return reverse('wireless:wirelesslan', args=[self.pk])


@extras_features('custom_fields', 'custom_links', 'export_templates', 'tags', 'webhooks')
class WirelessLink(WirelessAuthenticationBase, PrimaryModel):
    """
    A point-to-point connection between two wireless Interfaces.
    """
    interface_a = models.ForeignKey(
        to='dcim.Interface',
        limit_choices_to={'type__in': WIRELESS_IFACE_TYPES},
        on_delete=models.PROTECT,
        related_name='+'
    )
    interface_b = models.ForeignKey(
        to='dcim.Interface',
        limit_choices_to={'type__in': WIRELESS_IFACE_TYPES},
        on_delete=models.PROTECT,
        related_name='+'
    )
    ssid = models.CharField(
        max_length=SSID_MAX_LENGTH,
        blank=True,
        verbose_name='SSID'
    )
    status = models.CharField(
        max_length=50,
        choices=LinkStatusChoices,
        default=LinkStatusChoices.STATUS_CONNECTED
    )
    description = models.CharField(
        max_length=200,
        blank=True
    )

    # Cache the associated device for the A and B interfaces. This enables filtering of WirelessLinks by their
    # associated Devices.
    _interface_a_device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='+',
        blank=True,
        null=True
    )
    _interface_b_device = models.ForeignKey(
        to='dcim.Device',
        on_delete=models.CASCADE,
        related_name='+',
        blank=True,
        null=True
    )

    objects = RestrictedQuerySet.as_manager()

    clone_fields = ('ssid', 'status')

    class Meta:
        ordering = ['pk']
        unique_together = ('interface_a', 'interface_b')

    def __str__(self):
        return f'#{self.pk}'

    def get_absolute_url(self):
        return reverse('wireless:wirelesslink', args=[self.pk])

    def get_status_class(self):
        return LinkStatusChoices.CSS_CLASSES.get(self.status)

    def clean(self):

        # Validate interface types
        if self.interface_a.type not in WIRELESS_IFACE_TYPES:
            raise ValidationError({
                'interface_a': f"{self.interface_a.get_type_display()} is not a wireless interface."
            })
        if self.interface_b.type not in WIRELESS_IFACE_TYPES:
            raise ValidationError({
                'interface_a': f"{self.interface_b.get_type_display()} is not a wireless interface."
            })

    def save(self, *args, **kwargs):

        # Store the parent Device for the A and B interfaces
        self._interface_a_device = self.interface_a.device
        self._interface_b_device = self.interface_b.device

        super().save(*args, **kwargs)
