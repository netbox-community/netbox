from django import forms
from django.utils.translation import gettext as _

from dcim.models import Device, DeviceRole, Platform, Region, Site, SiteGroup
from extras.forms import LocalConfigContextFilterForm
from ipam.models import L2VPN, VRF
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import ContactModelFilterForm, TenancyFilterForm
from utilities.forms import (
    DynamicModelMultipleChoiceField, MultipleChoiceField, StaticSelect, TagFilterField, BOOLEAN_WITH_BLANK_CHOICES,
)
from virtualization.choices import *
from virtualization.models import *

__all__ = (
    'ClusterFilterForm',
    'ClusterGroupFilterForm',
    'ClusterTypeFilterForm',
    'VirtualMachineFilterForm',
    'VMInterfaceFilterForm',
)


class ClusterTypeFilterForm(NetBoxModelFilterSetForm):
    model = ClusterType
    tag = TagFilterField(model)


class ClusterGroupFilterForm(ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = ClusterGroup
    tag = TagFilterField(model)
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        ('Contacts', ('contact', 'contact_role', 'contact_group')),
    )


class ClusterFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Cluster
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        ('Attributes', ('group_id', 'type_id', 'status')),
        ('Location', ('region_id', 'site_group_id', 'site_id')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
        ('Contacts', ('contact', 'contact_role', 'contact_group')),
    )
    type_id = DynamicModelMultipleChoiceField(
        queryset=ClusterType.objects.all(),
        required=False,
        label=_('Type')
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    status = MultipleChoiceField(
        choices=ClusterStatusChoices,
        required=False
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
        },
        label=_('Site')
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Group')
    )
    tag = TagFilterField(model)


class VirtualMachineFilterForm(
    LocalConfigContextFilterForm,
    TenancyFilterForm,
    ContactModelFilterForm,
    NetBoxModelFilterSetForm
):
    model = VirtualMachine
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        ('Cluster', ('cluster_group_id', 'cluster_type_id', 'cluster_id', 'device_id')),
        ('Location', ('region_id', 'site_group_id', 'site_id')),
        ('Attributes', ('status', 'role_id', 'platform_id', 'mac_address', 'has_primary_ip', 'local_context_data')),
        ('Tenant', ('tenant_group_id', 'tenant_id')),
        ('Contacts', ('contact', 'contact_role', 'contact_group')),
    )
    cluster_group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Cluster group')
    )
    cluster_type_id = DynamicModelMultipleChoiceField(
        queryset=ClusterType.objects.all(),
        required=False,
        null_option='None',
        label=_('Cluster type')
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label=_('Cluster')
    )
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label=_('Device')
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site')
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'vm_role': "True"
        },
        label=_('Role')
    )
    status = MultipleChoiceField(
        choices=VirtualMachineStatusChoices,
        required=False
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        null_option='None',
        label=_('Platform')
    )
    mac_address = forms.CharField(
        required=False,
        label=_('MAC address')
    )
    has_primary_ip = forms.NullBooleanField(
        required=False,
        label=_('Has a primary IP'),
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class VMInterfaceFilterForm(NetBoxModelFilterSetForm):
    model = VMInterface
    fieldsets = (
        (None, ('q', 'filter_id', 'tag')),
        ('Virtual Machine', ('cluster_id', 'virtual_machine_id')),
        ('Attributes', ('enabled', 'mac_address', 'vrf_id', 'l2vpn_id')),
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label=_('Cluster')
    )
    virtual_machine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        query_params={
            'cluster_id': '$cluster_id'
        },
        label=_('Virtual machine')
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC address'
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label='VRF'
    )
    l2vpn_id = DynamicModelMultipleChoiceField(
        queryset=L2VPN.objects.all(),
        required=False,
        label=_('L2VPN')
    )
    tag = TagFilterField(model)
