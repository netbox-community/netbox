from dcim.choices import InterfaceModeChoices
from dcim.models import DeviceRole, Platform, Site
from extras.forms import CustomFieldModelCSVForm
from tenancy.models import Tenant
from utilities.forms import CSVChoiceField, CSVModelChoiceField, SlugField
from virtualization.choices import *
from virtualization.models import *

__all__ = (
    'ClusterCSVForm',
    'ClusterGroupCSVForm',
    'ClusterTypeCSVForm',
    'VirtualMachineCSVForm',
    'VMInterfaceCSVForm',
)


class ClusterTypeCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = ClusterType
        fields = ('name', 'slug', 'description')


class ClusterGroupCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = ClusterGroup
        fields = ('name', 'slug', 'description')


class ClusterCSVForm(CustomFieldModelCSVForm):
    type = CSVModelChoiceField(
        queryset=ClusterType.objects.all(),
        to_field_name='name',
        help_text='Type of cluster'
    )
    group = CSVModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Assigned cluster group'
    )
    site = CSVModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Assigned site'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Assigned tenant'
    )

    class Meta:
        model = Cluster
        fields = ('name', 'type', 'group', 'site', 'comments')


class VirtualMachineCSVForm(CustomFieldModelCSVForm):
    status = CSVChoiceField(
        choices=VirtualMachineStatusChoices,
        help_text='Operational status of device'
    )
    cluster = CSVModelChoiceField(
        queryset=Cluster.objects.all(),
        to_field_name='name',
        help_text='Assigned cluster'
    )
    role = CSVModelChoiceField(
        queryset=DeviceRole.objects.filter(
            vm_role=True
        ),
        required=False,
        to_field_name='name',
        help_text='Functional role'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )
    platform = CSVModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned platform'
    )

    class Meta:
        model = VirtualMachine
        fields = (
            'name', 'status', 'role', 'cluster', 'tenant', 'platform', 'vcpus', 'memory', 'disk', 'comments',
        )


class VMInterfaceCSVForm(CustomFieldModelCSVForm):
    virtual_machine = CSVModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        to_field_name='name'
    )
    mode = CSVChoiceField(
        choices=InterfaceModeChoices,
        required=False,
        help_text='IEEE 802.1Q operational mode (for L2 interfaces)'
    )

    class Meta:
        model = VMInterface
        fields = (
            'virtual_machine', 'name', 'enabled', 'mac_address', 'mtu', 'description', 'mode',
        )

    def clean_enabled(self):
        # Make sure enabled is True when it's not included in the uploaded data
        if 'enabled' not in self.data:
            return True
        else:
            return self.cleaned_data['enabled']
