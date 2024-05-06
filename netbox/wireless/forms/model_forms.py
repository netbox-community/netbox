from django.forms import PasswordInput
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, Interface, Location, Site
from ipam.models import VLAN
from netbox.forms import NetBoxModelForm
from tenancy.forms import TenancyForm
from utilities.forms.fields import CommentField, DynamicModelChoiceField, SlugField
from utilities.forms.rendering import FieldSet
from wireless.models import *

__all__ = (
    'WirelessLANForm',
    'WirelessLANGroupForm',
    'WirelessLinkForm',
)


class WirelessLANGroupForm(NetBoxModelForm):
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=WirelessLANGroup.objects.all(),
        required=False
    )
    slug = SlugField()

    fieldsets = (
        FieldSet('parent', 'name', 'slug', 'description', 'tags', name=_('Wireless LAN Group')),
    )

    class Meta:
        model = WirelessLANGroup
        fields = [
            'parent', 'name', 'slug', 'description', 'tags',
        ]


class WirelessLANForm(TenancyForm, NetBoxModelForm):
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=WirelessLANGroup.objects.all(),
        required=False
    )
    vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        selector=True,
        label=_('VLAN')
    )
    comments = CommentField()

    fieldsets = (
        FieldSet('ssid', 'group', 'vlan', 'status', 'description', 'tags', name=_('Wireless LAN')),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
        FieldSet('auth_type', 'auth_cipher', 'auth_psk', name=_('Authentication')),
    )

    class Meta:
        model = WirelessLAN
        fields = [
            'ssid', 'group', 'status', 'vlan', 'tenant_group', 'tenant', 'auth_type', 'auth_cipher', 'auth_psk',
            'description', 'comments', 'tags',
        ]
        widgets = {
            'auth_psk': PasswordInput(
                render_value=True,
                attrs={'data-toggle': 'password'}
            ),
        }


class WirelessLinkForm(TenancyForm, NetBoxModelForm):
    site_a = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Site'),
        initial_params={
            'devices': '$device_a',
        }
    )
    location_a = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        query_params={
            'site_id': '$site_a',
        },
        required=False,
        label=_('Location'),
        initial_params={
            'devices': '$device_a',
        }
    )
    device_a = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={
            'site_id': '$site_a',
            'location_id': '$location_a',
        },
        required=False,
        label=_('Device'),
        initial_params={
            'interfaces': '$interface_a'
        }
    )
    interface_a = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        query_params={
            'kind': 'wireless',
            'device_id': '$device_a',
        },
        context={
            'disabled': '_occupied',
        },
        label=_('Interface')
    )
    site_b = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label=_('Site'),
        initial_params={
            'devices': '$device_b',
        }
    )
    location_b = DynamicModelChoiceField(
        queryset=Location.objects.all(),
        query_params={
            'site_id': '$site_b',
        },
        required=False,
        label=_('Location'),
        initial_params={
            'devices': '$device_b',
        }
    )
    device_b = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        query_params={
            'site_id': '$site_b',
            'location_id': '$location_b',
        },
        required=False,
        label=_('Device'),
        initial_params={
            'interfaces': '$interface_b'
        }
    )
    interface_b = DynamicModelChoiceField(
        queryset=Interface.objects.all(),
        query_params={
            'kind': 'wireless',
            'device_id': '$device_b',
        },
        context={
            'disabled': '_occupied',
        },
        label=_('Interface')
    )
    comments = CommentField()

    fieldsets = (
        FieldSet('site_a', 'location_a', 'device_a', 'interface_a', name=_('Side A')),
        FieldSet('site_b', 'location_b', 'device_b', 'interface_b', name=_('Side B')),
        FieldSet('status', 'ssid', 'description', 'tags', name=_('Link')),
        FieldSet('tenant_group', 'tenant', name=_('Tenancy')),
        FieldSet('auth_type', 'auth_cipher', 'auth_psk', name=_('Authentication')),
    )

    class Meta:
        model = WirelessLink
        fields = [
            'site_a', 'location_a', 'device_a', 'interface_a', 'site_b', 'location_b', 'device_b', 'interface_b',
            'status', 'ssid', 'tenant_group', 'tenant', 'auth_type', 'auth_cipher', 'auth_psk', 'description',
            'comments', 'tags',
        ]
        widgets = {
            'auth_psk': PasswordInput(
                render_value=True,
                attrs={'data-toggle': 'password'}
            ),
        }
        labels = {
            'auth_type': 'Type',
            'auth_cipher': 'Cipher',
        }
