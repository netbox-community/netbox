from django import forms
from django.utils.translation import gettext_lazy as _

from dcim.choices import InterfaceModeChoices
from dcim.constants import INTERFACE_MTU_MAX, INTERFACE_MTU_MIN
from dcim.forms.mixins import ScopedBulkEditForm
from dcim.models import Device, DeviceRole, Platform, Site
from extras.models import ConfigTemplate
from ipam.models import VLAN, VLANGroup, VRF
from netbox.forms import NetBoxModelBulkEditForm
from tenancy.models import Tenant
from utilities.forms import BulkRenameForm, add_blank_choice
from utilities.forms.fields import CommentField, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import BulkEditNullBooleanSelect
from virtualization.choices import *
from virtualization.models import *

__all__ = (
    'ClusterBulkEditForm',
    'ClusterGroupBulkEditForm',
    'ClusterTypeBulkEditForm',
    'VirtualDiskBulkEditForm',
    'VirtualDiskBulkRenameForm',
    'VirtualMachineBulkEditForm',
    'VMInterfaceBulkEditForm',
    'VMInterfaceBulkRenameForm',
)


class ClusterTypeBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = ClusterType
    fieldsets = (
        FieldSet('description'),
    )
    nullable_fields = ('description',)


class ClusterGroupBulkEditForm(NetBoxModelBulkEditForm):
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )

    model = ClusterGroup
    fieldsets = (
        FieldSet('description'),
    )
    nullable_fields = ('description',)


class ClusterBulkEditForm(ScopedBulkEditForm, NetBoxModelBulkEditForm):
    type = DynamicModelChoiceField(
        label=_('Type'),
        queryset=ClusterType.objects.all(),
        required=False
    )
    group = DynamicModelChoiceField(
        label=_('Group'),
        queryset=ClusterGroup.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(ClusterStatusChoices),
        required=False,
        initial=''
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    comments = CommentField()

    model = Cluster
    fieldsets = (
        FieldSet('type', 'group', 'status', 'tenant', 'description'),
        FieldSet('scope_type', 'scope', name=_('Scope')),
    )
    nullable_fields = (
        'group', 'scope', 'tenant', 'description', 'comments',
    )


class VirtualMachineBulkEditForm(NetBoxModelBulkEditForm):
    status = forms.ChoiceField(
        label=_('Status'),
        choices=add_blank_choice(VirtualMachineStatusChoices),
        required=False,
        initial='',
    )
    site = DynamicModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        required=False
    )
    cluster = DynamicModelChoiceField(
        label=_('Cluster'),
        queryset=Cluster.objects.all(),
        required=False,
        query_params={
            'site_id': '$site'
        }
    )
    device = DynamicModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        required=False,
        query_params={
            'cluster_id': '$cluster'
        }
    )
    role = DynamicModelChoiceField(
        label=_('Role'),
        queryset=DeviceRole.objects.filter(
            vm_role=True
        ),
        required=False,
        query_params={
            "vm_role": "True"
        }
    )
    tenant = DynamicModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False
    )
    platform = DynamicModelChoiceField(
        label=_('Platform'),
        queryset=Platform.objects.all(),
        required=False
    )
    vcpus = forms.IntegerField(
        required=False,
        label=_('vCPUs')
    )
    memory = forms.IntegerField(
        required=False,
        label=_('Memory (MB)')
    )
    disk = forms.IntegerField(
        required=False,
        label=_('Disk (MB)')
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=200,
        required=False
    )
    config_template = DynamicModelChoiceField(
        queryset=ConfigTemplate.objects.all(),
        required=False
    )
    comments = CommentField()

    model = VirtualMachine
    fieldsets = (
        FieldSet('site', 'cluster', 'device', 'status', 'role', 'tenant', 'platform', 'description'),
        FieldSet('vcpus', 'memory', 'disk', name=_('Resources')),
        FieldSet('config_template', name=_('Configuration')),
    )
    nullable_fields = (
        'site', 'cluster', 'device', 'role', 'tenant', 'platform', 'vcpus', 'memory', 'disk', 'description', 'comments',
    )


class VMInterfaceBulkEditForm(NetBoxModelBulkEditForm):
    virtual_machine = forms.ModelChoiceField(
        label=_('Virtual machine'),
        queryset=VirtualMachine.objects.all(),
        required=False,
        disabled=True,
        widget=forms.HiddenInput()
    )
    parent = DynamicModelChoiceField(
        label=_('Parent'),
        queryset=VMInterface.objects.all(),
        required=False
    )
    bridge = DynamicModelChoiceField(
        label=_('Bridge'),
        queryset=VMInterface.objects.all(),
        required=False
    )
    enabled = forms.NullBooleanField(
        label=_('Enabled'),
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=INTERFACE_MTU_MIN,
        max_value=INTERFACE_MTU_MAX,
        label=_('MTU')
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=100,
        required=False
    )
    mode = forms.ChoiceField(
        label=_('Mode'),
        choices=add_blank_choice(InterfaceModeChoices),
        required=False
    )
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label=_('VLAN group')
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        query_params={
            'group_id': '$vlan_group',
        },
        label=_('Untagged VLAN')
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        query_params={
            'group_id': '$vlan_group',
        },
        label=_('Tagged VLANs')
    )
    vrf = DynamicModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        label=_('VRF')
    )

    model = VMInterface
    fieldsets = (
        FieldSet('mtu', 'enabled', 'vrf', 'description'),
        FieldSet('parent', 'bridge', name=_('Related Interfaces')),
        FieldSet('mode', 'vlan_group', 'untagged_vlan', 'tagged_vlans', name=_('802.1Q Switching')),
    )
    nullable_fields = (
        'parent', 'bridge', 'mtu', 'vrf', 'description',
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'virtual_machine' in self.initial:
            vm_id = self.initial.get('virtual_machine')

            # Restrict parent/bridge interface assignment by VM
            self.fields['parent'].widget.add_query_param('virtual_machine_id', vm_id)
            self.fields['bridge'].widget.add_query_param('virtual_machine_id', vm_id)

            # Limit VLAN choices by virtual machine
            self.fields['untagged_vlan'].widget.add_query_param('available_on_virtualmachine', vm_id)
            self.fields['tagged_vlans'].widget.add_query_param('available_on_virtualmachine', vm_id)

        else:
            # See 5643
            if 'pk' in self.initial:
                site = None
                interfaces = VMInterface.objects.filter(
                    pk__in=self.initial['pk']
                ).prefetch_related(
                    'virtual_machine__site'
                )

                # Check interface sites.  First interface should set site, further interfaces will either continue the
                # loop or reset back to no site and break the loop.
                for interface in interfaces:
                    vm_site = interface.virtual_machine.site or interface.virtual_machine.cluster._site
                    if site is None:
                        site = vm_site
                    elif vm_site is not site:
                        site = None
                        break

                if site is not None:
                    self.fields['untagged_vlan'].widget.add_query_param('site_id', site.pk)
                    self.fields['tagged_vlans'].widget.add_query_param('site_id', site.pk)

            self.fields['parent'].choices = ()
            self.fields['parent'].widget.attrs['disabled'] = True
            self.fields['bridge'].choices = ()
            self.fields['bridge'].widget.attrs['disabled'] = True


class VMInterfaceBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=VMInterface.objects.all(),
        widget=forms.MultipleHiddenInput()
    )


class VirtualDiskBulkEditForm(NetBoxModelBulkEditForm):
    virtual_machine = forms.ModelChoiceField(
        label=_('Virtual machine'),
        queryset=VirtualMachine.objects.all(),
        required=False,
        disabled=True,
        widget=forms.HiddenInput()
    )
    size = forms.IntegerField(
        required=False,
        label=_('Size (MB)')
    )
    description = forms.CharField(
        label=_('Description'),
        max_length=100,
        required=False
    )

    model = VirtualDisk
    fieldsets = (
        FieldSet('size', 'description'),
    )
    nullable_fields = ('description',)


class VirtualDiskBulkRenameForm(BulkRenameForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=VirtualDisk.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
