from django.utils.translation import gettext_lazy as _

from dcim.choices import InterfaceModeChoices
from dcim.forms.mixins import ScopedImportForm
from dcim.models import Device, DeviceRole, Platform, Site
from extras.models import ConfigTemplate
from ipam.models import VRF
from netbox.forms import NetBoxModelImportForm
from tenancy.models import Tenant
from utilities.forms.fields import CSVChoiceField, CSVModelChoiceField, SlugField
from virtualization.choices import *
from virtualization.models import *

__all__ = (
    'ClusterImportForm',
    'ClusterGroupImportForm',
    'ClusterTypeImportForm',
    'VirtualDiskImportForm',
    'VirtualMachineImportForm',
    'VMInterfaceImportForm',
)


class ClusterTypeImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = ClusterType
        fields = ('name', 'slug', 'description', 'tags')


class ClusterGroupImportForm(NetBoxModelImportForm):
    slug = SlugField()

    class Meta:
        model = ClusterGroup
        fields = ('name', 'slug', 'description', 'tags')


class ClusterImportForm(ScopedImportForm, NetBoxModelImportForm):
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
        fields = ('name', 'type', 'group', 'status', 'scope_type', 'scope_id', 'tenant', 'description', 'comments', 'tags')
        labels = {
            'scope_id': _('Scope ID'),
        }


class VirtualMachineImportForm(NetBoxModelImportForm):
    status = CSVChoiceField(
        label=_('Status'),
        choices=VirtualMachineStatusChoices,
        help_text=_('Operational status')
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
            'name', 'status', 'role', 'site', 'cluster', 'device', 'tenant', 'platform', 'vcpus', 'memory', 'disk',
            'description', 'serial', 'config_template', 'comments', 'tags',
        )


class VMInterfaceImportForm(NetBoxModelImportForm):
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
        help_text=_('Parent interface')
    )
    bridge = CSVModelChoiceField(
        label=_('Bridge'),
        queryset=VMInterface.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Bridged interface')
    )
    mode = CSVChoiceField(
        label=_('Mode'),
        choices=InterfaceModeChoices,
        required=False,
        help_text=_('IEEE 802.1Q operational mode (for L2 interfaces)')
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
            'virtual_machine', 'name', 'parent', 'bridge', 'enabled', 'mtu', 'description', 'mode',
            'vrf', 'tags'
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

    def clean_enabled(self):
        # Make sure enabled is True when it's not included in the uploaded data
        if 'enabled' not in self.data:
            return True
        else:
            return self.cleaned_data['enabled']


class VirtualDiskImportForm(NetBoxModelImportForm):
    virtual_machine = CSVModelChoiceField(
        label=_('Virtual machine'),
        queryset=VirtualMachine.objects.all(),
        to_field_name='name'
    )

    class Meta:
        model = VirtualDisk
        fields = (
            'virtual_machine', 'name', 'size', 'description', 'tags'
        )
