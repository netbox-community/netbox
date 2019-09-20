from django import forms
from django.core.exceptions import ValidationError
from taggit.forms import TagField

from dcim.constants import IFACE_TYPE_VIRTUAL, IFACE_MODE_ACCESS, IFACE_MODE_TAGGED_ALL
from dcim.forms import INTERFACE_MODE_HELP_TEXT
from dcim.models import Device, DeviceRole, Interface, Platform, Rack, Region, Site
from extras.forms import AddRemoveTagsForm, CustomFieldBulkEditForm, CustomFieldForm, CustomFieldFilterForm
from ipam.models import IPAddress
from tenancy.forms import TenancyForm
from tenancy.forms import TenancyFilterForm
from tenancy.models import Tenant
from utilities.forms import (
    add_blank_choice, APISelect, APISelectMultiple, BootstrapMixin, BulkEditForm, BulkEditNullBooleanSelect,
    ChainedFieldsMixin, ChainedModelChoiceField, ChainedModelMultipleChoiceField, CommentField, ComponentForm,
    ConfirmationForm, CSVChoiceField, ExpandableNameField, FilterChoiceField, JSONField, SlugField,
    SmallTextarea, StaticSelect2, StaticSelect2Multiple
)
from .constants import VM_STATUS_CHOICES
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine

VIFACE_TYPE_CHOICES = (
    (IFACE_TYPE_VIRTUAL, 'Virtual'),
)


#
# Cluster types
#

class ClusterTypeForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterType
        fields = [
            'name', 'slug',
        ]


class ClusterTypeCSVForm(forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterType
        fields = ClusterType.csv_headers
        help_texts = {
            'name': 'Name of cluster type',
        }


#
# Cluster groups
#

class ClusterGroupForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterGroup
        fields = [
            'name', 'slug',
        ]


class ClusterGroupCSVForm(forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterGroup
        fields = ClusterGroup.csv_headers
        help_texts = {
            'name': 'Name of cluster group',
        }


#
# Clusters
#

class ClusterForm(BootstrapMixin, CustomFieldForm):
    comments = CommentField()
    tags = TagField(
        required=False
    )

    class Meta:
        model = Cluster
        fields = [
            'name', 'type', 'group', 'site', 'comments', 'tags',
        ]
        widgets = {
            'type': APISelect(
                api_url="/api/virtualization/cluster-types/"
            ),
            'group': APISelect(
                api_url="/api/virtualization/cluster-groups/"
            ),
            'site': APISelect(
                api_url="/api/dcim/sites/"
            ),
        }


class ClusterCSVForm(forms.ModelForm):
    type = forms.ModelChoiceField(
        queryset=ClusterType.objects.all(),
        to_field_name='name',
        help_text='Name of cluster type',
        error_messages={
            'invalid_choice': 'Invalid cluster type name.',
        }
    )
    group = forms.ModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Name of cluster group',
        error_messages={
            'invalid_choice': 'Invalid cluster group name.',
        }
    )
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        to_field_name='name',
        required=False,
        help_text='Name of assigned site',
        error_messages={
            'invalid_choice': 'Invalid site name.',
        }
    )

    class Meta:
        model = Cluster
        fields = Cluster.csv_headers


class ClusterBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = forms.ModelChoiceField(
        queryset=ClusterType.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/virtualization/cluster-types/"
        )
    )
    group = forms.ModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/virtualization/cluster-groups/"
        )
    )
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/sites/"
        )
    )
    comments = CommentField(
        widget=SmallTextarea()
    )

    class Meta:
        nullable_fields = [
            'group', 'site', 'comments',
        ]


class ClusterFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Cluster
    q = forms.CharField(required=False, label='Search')
    type = FilterChoiceField(
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/virtualization/cluster-types/",
            value_field='slug',
        )
    )
    group = FilterChoiceField(
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        null_label='-- None --',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/virtualization/cluster-groups/",
            value_field='slug',
            null_option=True,
        )
    )
    site = FilterChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        null_label='-- None --',
        required=False,
        widget=APISelectMultiple(
            api_url="/api/dcim/sites/",
            value_field='slug',
            null_option=True,
        )
    )


class ClusterAddDevicesForm(BootstrapMixin, ChainedFieldsMixin, forms.Form):
    region = forms.ModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/regions/",
            filter_for={
                "site": "region_id",
            },
            attrs={
                'nullable': 'true',
            }
        )
    )
    site = ChainedModelChoiceField(
        queryset=Site.objects.all(),
        chains=(
            ('region', 'region'),
        ),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/sites/',
            filter_for={
                "rack": "site_id",
                "devices": "site_id",
            }
        )
    )
    rack = ChainedModelChoiceField(
        queryset=Rack.objects.all(),
        chains=(
            ('site', 'site'),
        ),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/racks/',
            filter_for={
                "devices": "rack_id"
            },
            attrs={
                'nullable': 'true',
            }
        )
    )
    devices = ChainedModelMultipleChoiceField(
        queryset=Device.objects.filter(cluster__isnull=True),
        chains=(
            ('site', 'site'),
            ('rack', 'rack'),
        ),
        widget=APISelectMultiple(
            api_url='/api/dcim/devices/',
            display_field='display_name',
            disabled_indicator='cluster'
        )
    )

    class Meta:
        fields = [
            'region', 'site', 'rack', 'devices',
        ]

    def __init__(self, cluster, *args, **kwargs):

        self.cluster = cluster

        super().__init__(*args, **kwargs)

        self.fields['devices'].choices = []

    def clean(self):
        super().clean()

        # If the Cluster is assigned to a Site, all Devices must be assigned to that Site.
        if self.cluster.site is not None:
            for device in self.cleaned_data.get('devices', []):
                if device.site != self.cluster.site:
                    raise ValidationError({
                        'devices': "{} belongs to a different site ({}) than the cluster ({})".format(
                            device, device.site, self.cluster.site
                        )
                    })


class ClusterRemoveDevicesForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Device.objects.all(),
        widget=forms.MultipleHiddenInput()
    )


#
# Virtual Machines
#

class VirtualMachineForm(BootstrapMixin, TenancyForm, CustomFieldForm):
    cluster_group = forms.ModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        widget=APISelect(
            api_url='/api/virtualization/cluster-groups/',
            filter_for={
                "cluster": "group_id",
            },
            attrs={
                'nullable': 'true',
            }
        )
    )
    cluster = ChainedModelChoiceField(
        queryset=Cluster.objects.all(),
        chains=(
            ('group', 'cluster_group'),
        ),
        widget=APISelect(
            api_url='/api/virtualization/clusters/'
        )
    )
    tags = TagField(
        required=False
    )
    local_context_data = JSONField(
        required=False,
        label=''
    )

    class Meta:
        model = VirtualMachine
        fields = [
            'name', 'status', 'cluster_group', 'cluster', 'role', 'tenant_group', 'tenant', 'platform', 'primary_ip4',
            'primary_ip6', 'vcpus', 'memory', 'disk', 'comments', 'tags', 'local_context_data',
        ]
        help_texts = {
            'local_context_data': "Local config context data overwrites all sources contexts in the final rendered "
                                  "config context",
        }
        widgets = {
            "status": StaticSelect2(),
            "role": APISelect(
                api_url="/api/dcim/device-roles/",
                additional_query_params={
                    "vm_role": "True"
                }
            ),
            'primary_ip4': StaticSelect2(),
            'primary_ip6': StaticSelect2(),
            'platform': APISelect(
                api_url='/api/dcim/platforms/'
            )
        }

    def __init__(self, *args, **kwargs):

        # Initialize helper selector
        instance = kwargs.get('instance')
        if instance.pk and instance.cluster is not None:
            initial = kwargs.get('initial', {}).copy()
            initial['cluster_group'] = instance.cluster.group
            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)

        if self.instance.pk:

            # Compile list of choices for primary IPv4 and IPv6 addresses
            for family in [4, 6]:
                ip_choices = [(None, '---------')]
                # Collect interface IPs
                interface_ips = IPAddress.objects.prefetch_related('interface').filter(
                    family=family, interface__virtual_machine=self.instance
                )
                if interface_ips:
                    ip_choices.append(
                        ('Interface IPs', [
                            (ip.id, '{} ({})'.format(ip.address, ip.interface)) for ip in interface_ips
                        ])
                    )
                # Collect NAT IPs
                nat_ips = IPAddress.objects.prefetch_related('nat_inside').filter(
                    family=family, nat_inside__interface__virtual_machine=self.instance
                )
                if nat_ips:
                    ip_choices.append(
                        ('NAT IPs', [
                            (ip.id, '{} ({})'.format(ip.address, ip.nat_inside.address)) for ip in nat_ips
                        ])
                    )
                self.fields['primary_ip{}'.format(family)].choices = ip_choices

        else:

            # An object that doesn't exist yet can't have any IPs assigned to it
            self.fields['primary_ip4'].choices = []
            self.fields['primary_ip4'].widget.attrs['readonly'] = True
            self.fields['primary_ip6'].choices = []
            self.fields['primary_ip6'].widget.attrs['readonly'] = True


class VirtualMachineCSVForm(forms.ModelForm):
    status = CSVChoiceField(
        choices=VM_STATUS_CHOICES,
        required=False,
        help_text='Operational status of device'
    )
    cluster = forms.ModelChoiceField(
        queryset=Cluster.objects.all(),
        to_field_name='name',
        help_text='Name of parent cluster',
        error_messages={
            'invalid_choice': 'Invalid cluster name.',
        }
    )
    role = forms.ModelChoiceField(
        queryset=DeviceRole.objects.filter(
            vm_role=True
        ),
        required=False,
        to_field_name='name',
        help_text='Name of functional role',
        error_messages={
            'invalid_choice': 'Invalid role name.'
        }
    )
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned tenant',
        error_messages={
            'invalid_choice': 'Tenant not found.'
        }
    )
    platform = forms.ModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Name of assigned platform',
        error_messages={
            'invalid_choice': 'Invalid platform.',
        }
    )

    class Meta:
        model = VirtualMachine
        fields = VirtualMachine.csv_headers


class VirtualMachineBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(VM_STATUS_CHOICES),
        required=False,
        initial='',
        widget=StaticSelect2(),
    )
    cluster = forms.ModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        widget=APISelect(
            api_url='/api/virtualization/clusters/'
        )
    )
    role = forms.ModelChoiceField(
        queryset=DeviceRole.objects.filter(
            vm_role=True
        ),
        required=False,
        widget=APISelect(
            api_url="/api/dcim/device-roles/",
            additional_query_params={
                "vm_role": "True"
            }
        )
    )
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        widget=APISelect(
            api_url='/api/tenancy/tenants/'
        )
    )
    platform = forms.ModelChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/platforms/'
        )
    )
    vcpus = forms.IntegerField(
        required=False,
        label='vCPUs'
    )
    memory = forms.IntegerField(
        required=False,
        label='Memory (MB)'
    )
    disk = forms.IntegerField(
        required=False,
        label='Disk (GB)'
    )
    comments = CommentField(
        widget=SmallTextarea()
    )

    class Meta:
        nullable_fields = [
            'role', 'tenant', 'platform', 'vcpus', 'memory', 'disk', 'comments',
        ]


class VirtualMachineFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldFilterForm):
    model = VirtualMachine
    field_order = [
        'q', 'cluster_group', 'cluster_type', 'cluster_id', 'status', 'role', 'region', 'site', 'tenant_group',
        'tenant', 'platform', 'mac_address',
    ]
    q = forms.CharField(
        required=False,
        label='Search'
    )
    cluster_group = FilterChoiceField(
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        null_label='-- None --',
        widget=APISelectMultiple(
            api_url='/api/virtualization/cluster-groups/',
            value_field="slug",
            null_option=True,
        )
    )
    cluster_type = FilterChoiceField(
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        null_label='-- None --',
        widget=APISelectMultiple(
            api_url='/api/virtualization/cluster-types/',
            value_field="slug",
            null_option=True,
        )
    )
    cluster_id = FilterChoiceField(
        queryset=Cluster.objects.all(),
        label='Cluster',
        widget=APISelectMultiple(
            api_url='/api/virtualization/clusters/',
        )
    )
    region = FilterChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            api_url='/api/dcim/regions/',
            value_field="slug",
            null_option=True,
        )
    )
    site = FilterChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        null_label='-- None --',
        widget=APISelectMultiple(
            api_url='/api/dcim/sites/',
            value_field="slug",
            null_option=True,
        )
    )
    role = FilterChoiceField(
        queryset=DeviceRole.objects.filter(vm_role=True),
        to_field_name='slug',
        null_label='-- None --',
        widget=APISelectMultiple(
            api_url='/api/dcim/device-roles/',
            value_field="slug",
            null_option=True,
            additional_query_params={
                'vm_role': "True"
            }
        )
    )
    status = forms.MultipleChoiceField(
        choices=VM_STATUS_CHOICES,
        required=False,
        widget=StaticSelect2Multiple()
    )
    platform = FilterChoiceField(
        queryset=Platform.objects.all(),
        to_field_name='slug',
        null_label='-- None --',
        widget=APISelectMultiple(
            api_url='/api/dcim/platforms/',
            value_field="slug",
            null_option=True,
        )
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC address'
    )


#
# VM interfaces
#

class InterfaceForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(
        required=False
    )

    class Meta:
        model = Interface
        fields = [
            'virtual_machine', 'name', 'type', 'enabled', 'mac_address', 'mtu', 'description', 'mode', 'tags',
            'untagged_vlan', 'tagged_vlans',
        ]
        widgets = {
            'virtual_machine': forms.HiddenInput(),
            'type': forms.HiddenInput(),
            'mode': StaticSelect2()
        }
        labels = {
            'mode': '802.1Q Mode',
        }
        help_texts = {
            'mode': INTERFACE_MODE_HELP_TEXT,
        }

    def clean(self):
        super().clean()

        # Validate VLAN assignments
        tagged_vlans = self.cleaned_data['tagged_vlans']

        # Untagged interfaces cannot be assigned tagged VLANs
        if self.cleaned_data['mode'] == IFACE_MODE_ACCESS and tagged_vlans:
            raise forms.ValidationError({
                'mode': "An access interface cannot have tagged VLANs assigned."
            })

        # Remove all tagged VLAN assignments from "tagged all" interfaces
        elif self.cleaned_data['mode'] == IFACE_MODE_TAGGED_ALL:
            self.cleaned_data['tagged_vlans'] = []


class InterfaceCreateForm(ComponentForm):
    name_pattern = ExpandableNameField(
        label='Name'
    )
    type = forms.ChoiceField(
        choices=VIFACE_TYPE_CHOICES,
        initial=IFACE_TYPE_VIRTUAL,
        widget=forms.HiddenInput()
    )
    enabled = forms.BooleanField(
        required=False
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=32767,
        label='MTU'
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC Address'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    tags = TagField(
        required=False
    )

    def __init__(self, *args, **kwargs):

        # Set interfaces enabled by default
        kwargs['initial'] = kwargs.get('initial', {}).copy()
        kwargs['initial'].update({'enabled': True})

        super().__init__(*args, **kwargs)


class InterfaceBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=32767,
        label='MTU'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )

    class Meta:
        nullable_fields = [
            'mtu', 'description',
        ]


#
# Bulk VirtualMachine component creation
#

class VirtualMachineBulkAddComponentForm(BootstrapMixin, forms.Form):
    pk = forms.ModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )


class VirtualMachineBulkAddInterfaceForm(VirtualMachineBulkAddComponentForm):
    type = forms.ChoiceField(
        choices=VIFACE_TYPE_CHOICES,
        initial=IFACE_TYPE_VIRTUAL,
        widget=forms.HiddenInput()
    )
    enabled = forms.BooleanField(
        required=False,
        initial=True
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=32767,
        label='MTU'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
