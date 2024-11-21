from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.models import Device, DeviceRole, Location, Platform, Region, Site, SiteGroup
from extras.forms import LocalConfigContextFilterForm
from extras.models import ConfigTemplate
from ipam.models import VRF
from netbox.forms import NetBoxModelFilterSetForm
from tenancy.forms import ContactModelFilterForm, TenancyFilterForm
from utilities.forms import BOOLEAN_WITH_BLANK_CHOICES
from utilities.forms.fields import DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet
from virtualization.choices import *
from virtualization.models import *
from vpn.models import L2VPN

__all__ = (
    'ClusterFilterForm',
    'ClusterGroupFilterForm',
    'ClusterTypeFilterForm',
    'VirtualDiskFilterForm',
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
    )


class ClusterFilterForm(TenancyFilterForm, ContactModelFilterForm, NetBoxModelFilterSetForm):
    model = Cluster
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('group_id', 'type_id', 'status', name=_('Attributes')),
        FieldSet('region_id', 'site_group_id', 'site_id', 'location_id', name=_('Scope')),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
    )
    selector_fields = ('filter_id', 'q', 'group_id')
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
    location_id = DynamicModelMultipleChoiceField(
        queryset=Location.objects.all(),
        required=False,
        label=_('Location')
    )
    status = forms.MultipleChoiceField(
        label=_('Status'),
        choices=ClusterStatusChoices,
        required=False
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
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('cluster_group_id', 'cluster_type_id', 'cluster_id', 'device_id', name=_('Cluster')),
        FieldSet('region_id', 'site_group_id', 'site_id', name=_('Location')),
        FieldSet(
            'status', 'role_id', 'platform_id', 'mac_address', 'has_primary_ip', 'config_template_id',
            'local_context_data', 'serial', name=_('Attributes')
        ),
        FieldSet('tenant_group_id', 'tenant_id', name=_('Tenant')),
        FieldSet('contact', 'contact_role', 'contact_group', name=_('Contacts')),
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
    status = forms.MultipleChoiceField(
        label=_('Status'),
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
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    serial = forms.CharField(
        required=False,
        label=_('Serial number')
    )
    config_template_id = DynamicModelMultipleChoiceField(
        queryset=ConfigTemplate.objects.all(),
        required=False,
        label=_('Config template')
    )
    tag = TagFilterField(model)


class VMInterfaceFilterForm(NetBoxModelFilterSetForm):
    model = VMInterface
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('cluster_id', 'virtual_machine_id', name=_('Virtual Machine')),
        FieldSet('enabled', 'mac_address', 'vrf_id', 'l2vpn_id', name=_('Attributes')),
    )
    selector_fields = ('filter_id', 'q', 'virtual_machine_id')
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
        label=_('Enabled'),
        required=False,
        widget=forms.Select(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mac_address = forms.CharField(
        required=False,
        label=_('MAC address')
    )
    vrf_id = DynamicModelMultipleChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )
    l2vpn_id = DynamicModelMultipleChoiceField(
        queryset=L2VPN.objects.all(),
        required=False,
        label=_('L2VPN')
    )
    tag = TagFilterField(model)


class VirtualDiskFilterForm(NetBoxModelFilterSetForm):
    model = VirtualDisk
    fieldsets = (
        FieldSet('q', 'filter_id', 'tag'),
        FieldSet('virtual_machine_id', name=_('Virtual Machine')),
        FieldSet('size', name=_('Attributes')),
    )
    virtual_machine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label=_('Virtual machine')
    )
    size = forms.IntegerField(
        label=_('Size (MB)'),
        required=False,
        min_value=1
    )
    tag = TagFilterField(model)
