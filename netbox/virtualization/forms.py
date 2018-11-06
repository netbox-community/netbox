from __future__ import unicode_literals

from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Count
from mptt.forms import TreeNodeChoiceField
from taggit.forms import TagField

from dcim.constants import IFACE_FF_VIRTUAL, IFACE_MODE_ACCESS, IFACE_MODE_TAGGED_ALL
from dcim.forms import INTERFACE_MODE_HELP_TEXT
from dcim.models import Device, DeviceRole, Interface, Platform, Rack, Region, Site
from extras.forms import AddRemoveTagsForm, CustomFieldBulkEditForm, CustomFieldForm, CustomFieldFilterForm
from ipam.models import IPAddress
from tenancy.forms import TenancyForm
from tenancy.models import Tenant
from utilities.forms import (
    AnnotatedMultipleChoiceField, APISelect, APISelectMultiple, BootstrapMixin, BulkEditForm, BulkEditNullBooleanSelect,
    ChainedFieldsMixin, ChainedModelChoiceField, ChainedModelMultipleChoiceField, CommentField, ComponentForm,
    ConfirmationForm, CSVChoiceField, ExpandableNameField, FilterChoiceField, FilterTreeNodeMultipleChoiceField,
    JSONField, SlugField, SmallTextarea, add_blank_choice,
)
from .constants import VM_STATUS_CHOICES
from .models import Cluster, ClusterGroup, ClusterType, VirtualMachine

VIFACE_FF_CHOICES = (
    (IFACE_FF_VIRTUAL, 'Virtual'),
)


#
# Cluster types
#

class ClusterTypeForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterType
        fields = ['name', 'slug']


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
        fields = ['name', 'slug']


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
    comments = CommentField(widget=SmallTextarea)
    tags = TagField(required=False)

    class Meta:
        model = Cluster
        fields = ['name', 'type', 'group', 'site', 'comments', 'tags']


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
    pk = forms.ModelMultipleChoiceField(queryset=Cluster.objects.all(), widget=forms.MultipleHiddenInput)
    type = forms.ModelChoiceField(queryset=ClusterType.objects.all(), required=False)
    group = forms.ModelChoiceField(queryset=ClusterGroup.objects.all(), required=False)
    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=False)
    comments = CommentField(widget=SmallTextarea)

    class Meta:
        nullable_fields = ['group', 'site', 'comments']


class ClusterFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Cluster
    q = forms.CharField(required=False, label='Search')
    type = FilterChoiceField(
        queryset=ClusterType.objects.annotate(filter_count=Count('clusters')),
        to_field_name='slug',
        required=False,
    )
    group = FilterChoiceField(
        queryset=ClusterGroup.objects.annotate(filter_count=Count('clusters')),
        to_field_name='slug',
        null_label='-- None --',
        required=False,
    )
    site = FilterChoiceField(
        queryset=Site.objects.annotate(filter_count=Count('clusters')),
        to_field_name='slug',
        null_label='-- None --',
        required=False,
    )


class ClusterAddDevicesForm(BootstrapMixin, ChainedFieldsMixin, forms.Form):
    region = TreeNodeChoiceField(
        queryset=Region.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={'filter-for': 'site', 'nullable': 'true'}
        )
    )
    site = ChainedModelChoiceField(
        queryset=Site.objects.all(),
        chains=(
            ('region', 'region'),
        ),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/sites/?region_id={{region}}',
            attrs={'filter-for': 'rack'}
        )
    )
    rack = ChainedModelChoiceField(
        queryset=Rack.objects.all(),
        chains=(
            ('site', 'site'),
        ),
        required=False,
        widget=APISelect(
            api_url='/api/dcim/racks/?site_id={{site}}',
            attrs={'filter-for': 'devices', 'nullable': 'true'}
        )
    )
    devices = ChainedModelMultipleChoiceField(
        queryset=Device.objects.filter(cluster__isnull=True),
        chains=(
            ('site', 'site'),
            ('rack', 'rack'),
        ),
        widget=APISelectMultiple(
            api_url='/api/dcim/devices/?site_id={{site}}&rack_id={{rack}}',
            display_field='display_name',
            disabled_indicator='cluster'
        )
    )

    class Meta:
        fields = ['region', 'site', 'rack', 'devices']

    def __init__(self, cluster, *args, **kwargs):

        self.cluster = cluster

        super(ClusterAddDevicesForm, self).__init__(*args, **kwargs)

        self.fields['devices'].choices = []

    def clean(self):

        super(ClusterAddDevicesForm, self).clean()

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
    pk = forms.ModelMultipleChoiceField(queryset=Device.objects.all(), widget=forms.MultipleHiddenInput)


#
# Virtual Machines
#

class VirtualMachineForm(BootstrapMixin, TenancyForm, CustomFieldForm):
    cluster_group = forms.ModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        widget=forms.Select(
            attrs={'filter-for': 'cluster', 'nullable': 'true'}
        )
    )
    cluster = ChainedModelChoiceField(
        queryset=Cluster.objects.all(),
        chains=(
            ('group', 'cluster_group'),
        ),
        widget=APISelect(
            api_url='/api/virtualization/clusters/?group_id={{cluster_group}}'
        )
    )
    tags = TagField(required=False)
    local_context_data = JSONField(required=False)

    class Meta:
        model = VirtualMachine
        fields = [
            'name', 'status', 'cluster_group', 'cluster', 'role', 'tenant', 'platform', 'primary_ip4', 'primary_ip6',
            'vcpus', 'memory', 'disk', 'comments', 'tags', 'local_context_data',
        ]
        help_texts = {
            'local_context_data': "Local config context data overwrites all sources contexts in the final rendered config context",
        }

    def __init__(self, *args, **kwargs):

        # Initialize helper selector
        instance = kwargs.get('instance')
        if instance.pk and instance.cluster is not None:
            initial = kwargs.get('initial', {}).copy()
            initial['cluster_group'] = instance.cluster.group
            kwargs['initial'] = initial

        super(VirtualMachineForm, self).__init__(*args, **kwargs)

        if self.instance.pk:

            # Compile list of choices for primary IPv4 and IPv6 addresses
            for family in [4, 6]:
                ip_choices = [(None, '---------')]
                # Collect interface IPs
                interface_ips = IPAddress.objects.select_related('interface').filter(
                    family=family, interface__virtual_machine=self.instance
                )
                if interface_ips:
                    ip_choices.append(
                        ('Interface IPs', [
                            (ip.id, '{} ({})'.format(ip.address, ip.interface)) for ip in interface_ips
                        ])
                    )
                # Collect NAT IPs
                nat_ips = IPAddress.objects.select_related('nat_inside').filter(
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
        queryset=DeviceRole.objects.filter(vm_role=True),
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
    pk = forms.ModelMultipleChoiceField(queryset=VirtualMachine.objects.all(), widget=forms.MultipleHiddenInput)
    status = forms.ChoiceField(choices=add_blank_choice(VM_STATUS_CHOICES), required=False, initial='')
    cluster = forms.ModelChoiceField(queryset=Cluster.objects.all(), required=False)
    role = forms.ModelChoiceField(queryset=DeviceRole.objects.filter(vm_role=True), required=False)
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False)
    platform = forms.ModelChoiceField(queryset=Platform.objects.all(), required=False)
    vcpus = forms.IntegerField(required=False, label='vCPUs')
    memory = forms.IntegerField(required=False, label='Memory (MB)')
    disk = forms.IntegerField(required=False, label='Disk (GB)')
    comments = CommentField(widget=SmallTextarea)

    class Meta:
        nullable_fields = ['role', 'tenant', 'platform', 'vcpus', 'memory', 'disk', 'comments']


class VirtualMachineFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = VirtualMachine
    q = forms.CharField(required=False, label='Search')
    cluster_group = FilterChoiceField(
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        null_label='-- None --'
    )
    cluster_type = FilterChoiceField(
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        null_label='-- None --'
    )
    cluster_id = FilterChoiceField(
        queryset=Cluster.objects.annotate(filter_count=Count('virtual_machines')),
        label='Cluster'
    )
    region = FilterTreeNodeMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
    )
    site = FilterChoiceField(
        queryset=Site.objects.annotate(filter_count=Count('clusters__virtual_machines')),
        to_field_name='slug',
        null_label='-- None --'
    )
    role = FilterChoiceField(
        queryset=DeviceRole.objects.filter(vm_role=True).annotate(filter_count=Count('virtual_machines')),
        to_field_name='slug',
        null_label='-- None --'
    )
    status = AnnotatedMultipleChoiceField(
        choices=VM_STATUS_CHOICES,
        annotate=VirtualMachine.objects.all(),
        annotate_field='status',
        required=False
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.annotate(filter_count=Count('virtual_machines')),
        to_field_name='slug',
        null_label='-- None --'
    )
    platform = FilterChoiceField(
        queryset=Platform.objects.annotate(filter_count=Count('virtual_machines')),
        to_field_name='slug',
        null_label='-- None --'
    )


#
# VM interfaces
#

class InterfaceForm(BootstrapMixin, forms.ModelForm):
    tags = TagField(required=False)

    class Meta:
        model = Interface
        fields = [
            'virtual_machine', 'name', 'form_factor', 'enabled', 'mac_address', 'mtu', 'description', 'mode', 'tags',
            'untagged_vlan', 'tagged_vlans',
        ]
        widgets = {
            'virtual_machine': forms.HiddenInput(),
            'form_factor': forms.HiddenInput(),
        }
        labels = {
            'mode': '802.1Q Mode',
        }
        help_texts = {
            'mode': INTERFACE_MODE_HELP_TEXT,
        }

    def clean(self):

        super(InterfaceForm, self).clean()

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
    name_pattern = ExpandableNameField(label='Name')
    form_factor = forms.ChoiceField(choices=VIFACE_FF_CHOICES, initial=IFACE_FF_VIRTUAL, widget=forms.HiddenInput())
    enabled = forms.BooleanField(required=False)
    mtu = forms.IntegerField(required=False, min_value=1, max_value=32767, label='MTU')
    mac_address = forms.CharField(required=False, label='MAC Address')
    description = forms.CharField(max_length=100, required=False)
    tags = TagField(required=False)

    def __init__(self, *args, **kwargs):

        # Set interfaces enabled by default
        kwargs['initial'] = kwargs.get('initial', {}).copy()
        kwargs['initial'].update({'enabled': True})

        super(InterfaceCreateForm, self).__init__(*args, **kwargs)


class InterfaceBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Interface.objects.all(), widget=forms.MultipleHiddenInput)
    enabled = forms.NullBooleanField(required=False, widget=BulkEditNullBooleanSelect)
    mtu = forms.IntegerField(required=False, min_value=1, max_value=32767, label='MTU')
    description = forms.CharField(max_length=100, required=False)

    class Meta:
        nullable_fields = ['mtu', 'description']


#
# Bulk VirtualMachine component creation
#

class VirtualMachineBulkAddComponentForm(BootstrapMixin, forms.Form):
    pk = forms.ModelMultipleChoiceField(queryset=VirtualMachine.objects.all(), widget=forms.MultipleHiddenInput)
    name_pattern = ExpandableNameField(label='Name')


class VirtualMachineBulkAddInterfaceForm(VirtualMachineBulkAddComponentForm):
    form_factor = forms.ChoiceField(choices=VIFACE_FF_CHOICES, initial=IFACE_FF_VIRTUAL, widget=forms.HiddenInput())
    enabled = forms.BooleanField(required=False, initial=True)
    mtu = forms.IntegerField(required=False, min_value=1, max_value=32767, label='MTU')
    description = forms.CharField(max_length=100, required=False)
