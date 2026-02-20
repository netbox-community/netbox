from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from dcim.choices import InterfaceModeChoices
from dcim.forms.mixins import ScopedImportForm
from dcim.models import Device, DeviceRole, Platform, Site
from extras.models import ConfigTemplate
from ipam.choices import VLANQinQRoleChoices
from ipam.models import VLAN, VRF, VLANGroup
from netbox.forms import NetBoxModelImportForm, OrganizationalModelImportForm, OwnerCSVMixin, PrimaryModelImportForm
from tenancy.models import Tenant
from utilities.forms.fields import CSVChoiceField, CSVModelChoiceField, CSVModelMultipleChoiceField
from virtualization.choices import *
from virtualization.models import *

__all__ = (
    'ClusterGroupImportForm',
    'ClusterImportForm',
    'ClusterTypeImportForm',
    'VMInterfaceImportForm',
    'VirtualDiskImportForm',
    'VirtualMachineImportForm',
)


class ClusterTypeImportForm(OrganizationalModelImportForm):

    class Meta:
        model = ClusterType
        fields = ('name', 'slug', 'description', 'owner', 'comments', 'tags')


class ClusterGroupImportForm(OrganizationalModelImportForm):

    class Meta:
        model = ClusterGroup
        fields = ('name', 'slug', 'description', 'owner', 'comments', 'tags')


class ClusterImportForm(ScopedImportForm, PrimaryModelImportForm):
    type = CSVModelChoiceField(
        label=_('Type'),
        queryset=ClusterType.objects.all(),
        to_field_name='name',
        help_text=_('Type of cluster')
    )
    group = CSVModelChoiceField(
        label=_('Group'),
        queryset=ClusterGroup.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned cluster group')
    )
    status = CSVChoiceField(
        label=_('Status'),
        choices=ClusterStatusChoices,
        help_text=_('Operational status')
    )
    site = CSVModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned site')
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = Cluster
        fields = (
            'name', 'type', 'group', 'status', 'scope_type', 'scope_id', 'tenant', 'description', 'owner', 'comments',
            'tags',
        )
        labels = {
            'scope_id': _('Scope ID'),
        }


class VirtualMachineImportForm(PrimaryModelImportForm):
    status = CSVChoiceField(
        label=_('Status'),
        choices=VirtualMachineStatusChoices,
        help_text=_('Operational status')
    )
    start_on_boot = CSVChoiceField(
        label=_('Start on boot'),
        choices=VirtualMachineStartOnBootChoices,
        help_text=_('Start on boot in hypervisor'),
        required=False,
    )
    site = CSVModelChoiceField(
        label=_('Site'),
        queryset=Site.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned site')
    )
    cluster = CSVModelChoiceField(
        label=_('Cluster'),
        queryset=Cluster.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned cluster')
    )
    device = CSVModelChoiceField(
        label=_('Device'),
        queryset=Device.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned device within cluster')
    )
    role = CSVModelChoiceField(
        label=_('Role'),
        queryset=DeviceRole.objects.filter(
            vm_role=True
        ),
        required=False,
        to_field_name='name',
        help_text=_('Functional role')
    )
    tenant = CSVModelChoiceField(
        label=_('Tenant'),
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )
    platform = CSVModelChoiceField(
        label=_('Platform'),
        queryset=Platform.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned platform')
    )
    config_template = CSVModelChoiceField(
        queryset=ConfigTemplate.objects.all(),
        to_field_name='name',
        required=False,
        label=_('Config template'),
        help_text=_('Config template')
    )

    class Meta:
        model = VirtualMachine
        fields = (
            'name', 'status', 'start_on_boot', 'role', 'site', 'cluster', 'device', 'tenant', 'platform', 'vcpus',
            'memory', 'disk', 'description', 'serial', 'config_template', 'comments', 'owner', 'tags',
        )


class VMInterfaceImportForm(OwnerCSVMixin, NetBoxModelImportForm):
    virtual_machine = CSVModelChoiceField(
        label=_('Virtual machine'),
        queryset=VirtualMachine.objects.all(),
        to_field_name='name'
    )
    parent = CSVModelChoiceField(
        label=_('Parent'),
        queryset=VMInterface.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent interface'),
    )
    bridge = CSVModelChoiceField(
        label=_('Bridge'),
        queryset=VMInterface.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Bridged interface'),
    )
    mode = CSVChoiceField(
        label=_('Mode'),
        choices=InterfaceModeChoices,
        required=False,
        help_text=_('IEEE 802.1Q operational mode (for L2 interfaces)'),
    )
    vlan_group = CSVModelChoiceField(
        label=_('VLAN group'),
        queryset=VLANGroup.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Filter VLANs available for assignment by group'),
    )
    untagged_vlan = CSVModelChoiceField(
        label=_('Untagged VLAN'),
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='vid',
        help_text=_('Assigned untagged VLAN ID (filtered by VLAN group)'),
    )
    tagged_vlans = CSVModelMultipleChoiceField(
        label=_('Tagged VLANs'),
        queryset=VLAN.objects.all(),
        required=False,
        to_field_name='vid',
        help_text=mark_safe(
            _(
                'Assigned tagged VLAN IDs separated by commas, encased with double quotes '
                '(filtered by VLAN group). Example:'
            )
            + ' <code>"100,200,300"</code>'
        ),
    )
    qinq_svlan = CSVModelChoiceField(
        label=_('Q-in-Q Service VLAN'),
        queryset=VLAN.objects.filter(qinq_role=VLANQinQRoleChoices.ROLE_SERVICE),
        required=False,
        to_field_name='vid',
        help_text=_('Assigned Q-in-Q Service VLAN ID (filtered by VLAN group)'),
    )
    vrf = CSVModelChoiceField(
        label=_('VRF'),
        queryset=VRF.objects.all(),
        required=False,
        to_field_name='rd',
        help_text=_('Assigned VRF')
    )

    class Meta:
        model = VMInterface
        fields = (
            'virtual_machine', 'name', 'parent', 'bridge', 'enabled', 'mtu', 'description', 'mode', 'vlan_group',
            'untagged_vlan', 'tagged_vlans', 'qinq_svlan', 'vrf', 'owner', 'tags',
        )

    def __init__(self, data=None, *args, **kwargs):
        super().__init__(data, *args, **kwargs)

        if data:
            # Limit interface choices for parent & bridge interfaces to the assigned VM
            if virtual_machine := data.get('virtual_machine'):
                params = {
                    f"virtual_machine__{self.fields['virtual_machine'].to_field_name}": virtual_machine
                }
                self.fields['parent'].queryset = self.fields['parent'].queryset.filter(**params)
                self.fields['bridge'].queryset = self.fields['bridge'].queryset.filter(**params)

            # Limit choices for VLANs to the assigned VLAN group
            if vlan_group := data.get('vlan_group'):
                params = {f"group__{self.fields['vlan_group'].to_field_name}": vlan_group}
                self.fields['untagged_vlan'].queryset = self.fields['untagged_vlan'].queryset.filter(**params)
                self.fields['tagged_vlans'].queryset = self.fields['tagged_vlans'].queryset.filter(**params)
                self.fields['qinq_svlan'].queryset = self.fields['qinq_svlan'].queryset.filter(**params)

    def clean_enabled(self):
        # Make sure enabled is True when it's not included in the uploaded data
        if 'enabled' not in self.data:
            return True
        return self.cleaned_data['enabled']


class VirtualDiskImportForm(OwnerCSVMixin, NetBoxModelImportForm):
    virtual_machine = CSVModelChoiceField(
        label=_('Virtual machine'),
        queryset=VirtualMachine.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = VirtualDisk
        fields = (
            'virtual_machine', 'name', 'size', 'description', 'owner', 'tags'
        )
