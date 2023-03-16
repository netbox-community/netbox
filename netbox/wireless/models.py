from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel

from dcim.choices import LinkStatusChoices
from dcim.constants import WIRELESS_IFACE_TYPES
from netbox.models import NestedGroupModel, PrimaryModel
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
        blank=True,
        verbose_name="Auth Type",
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

    class Meta:
        ordering = ('name', 'pk')
        constraints = (
            models.UniqueConstraint(
                fields=('parent', 'name'),
                name='%(app_label)s_%(class)s_unique_parent_name'
            ),
        )
        verbose_name = 'Wireless LAN Group'

    def get_absolute_url(self):
        return reverse('wireless:wirelesslangroup', args=[self.pk])


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
    status = models.CharField(
        max_length=50,
        choices=WirelessLANStatusChoices,
        default=WirelessLANStatusChoices.STATUS_ACTIVE
    )
    vlan = models.ForeignKey(
        to='ipam.VLAN',
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name='VLAN'
    )
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='wireless_lans',
        blank=True,
        null=True
    )

    clone_fields = ('ssid', 'group', 'tenant', 'description')

    class Meta:
        ordering = ('ssid', 'pk')
        verbose_name = 'Wireless LAN'

    def __str__(self):
        return self.ssid

    def get_absolute_url(self):
        return reverse('wireless:wirelesslan', args=[self.pk])

    def get_status_color(self):
        return WirelessLANStatusChoices.colors.get(self.status)


def get_wireless_interface_types():
    # Wrap choices in a callable to avoid generating dummy migrations
    # when the choices are updated.
    return {'type__in': WIRELESS_IFACE_TYPES}


class WirelessLink(WirelessAuthenticationBase, PrimaryModel):
    """
    A point-to-point connection between two wireless Interfaces.
    """
    interface_a = models.ForeignKey(
        to='dcim.Interface',
        limit_choices_to=get_wireless_interface_types,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="Interface A",
    )
    interface_b = models.ForeignKey(
        to='dcim.Interface',
        limit_choices_to=get_wireless_interface_types,
        on_delete=models.PROTECT,
        related_name='+',
        verbose_name="Interface B",
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
    tenant = models.ForeignKey(
        to='tenancy.Tenant',
        on_delete=models.PROTECT,
        related_name='wireless_links',
        blank=True,
        null=True
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

    clone_fields = ('ssid', 'status')

    class Meta:
        ordering = ['pk']
        constraints = (
            models.UniqueConstraint(
                fields=('interface_a', 'interface_b'),
                name='%(app_label)s_%(class)s_unique_interfaces'
            ),
        )

    def __str__(self):
        return self.ssid or f'#{self.pk}'

    def get_absolute_url(self):
        return reverse('wireless:wirelesslink', args=[self.pk])

    def get_status_color(self):
        return LinkStatusChoices.colors.get(self.status)

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
