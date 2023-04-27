from django.utils.translation import gettext as _

from dcim.choices import InterfaceModeChoices
from dcim.models import Device, DeviceRole, Platform, Site
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


class ClusterImportForm(NetBoxModelImportForm):
    type = CSVModelChoiceField(
        queryset=ClusterType.objects.all(),
        to_field_name='name',
        help_text=_('Type of cluster')
    )
    group = CSVModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned cluster group')
    )
    status = CSVChoiceField(
        choices=ClusterStatusChoices,
        help_text=_('Operational status')
    )
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned site')
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned tenant')
    )

    class Meta:
        model = Cluster
        fields = ('name', 'type', 'group', 'status', 'site', 'description', 'comments', 'tags')


class VirtualMachineImportForm(NetBoxModelImportForm):
    status = CSVChoiceField(
        choices=VirtualMachineStatusChoices,
        help_text=_('Operational status')
    )
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned site')
    )
    cluster = CSVModelChoiceField(
        queryset=Cluster.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned cluster')
    )
    device = CSVModelChoiceField(
        queryset=Device.objects.all(),
        to_field_name='name',
        required=False,
        help_text=_('Assigned device within cluster')
    )
    role = CSVModelChoiceField(
        queryset=DeviceRole.objects.filter(
            vm_role=True
        ),
        required=False,
        to_field_name='name',
        help_text=_('Functional role')
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned tenant')
    )
    platform = CSVModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Assigned platform')
    )

    class Meta:
        model = VirtualMachine
        fields = (
            'name', 'status', 'role', 'site', 'cluster', 'device', 'tenant', 'platform', 'vcpus', 'memory', 'disk',
            'description', 'comments', 'tags',
        )


class VMInterfaceImportForm(NetBoxModelImportForm):
    virtual_machine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        to_field_name='name'
    )
    parent = CSVModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Parent interface')
    )
    bridge = CSVModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        to_field_name='name',
        help_text=_('Bridged interface')
    )
    mode = CSVChoiceField(
        choices=InterfaceModeChoices,
        required=False,
        help_text=_('IEEE 802.1Q operational mode (for L2 interfaces)')
    )
    vrf = CSVModelChoiceField(
        queryset=VRF.objects.all(),
        required=False,
        to_field_name='rd',
        help_text=_('Assigned VRF')
    )

    class Meta:
        model = VMInterface
        fields = (
            'virtual_machine', 'name', 'parent', 'bridge', 'enabled', 'mac_address', 'mtu', 'description', 'mode',
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
