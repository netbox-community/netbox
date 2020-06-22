from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from dcim.choices import InterfaceModeChoices
from dcim.constants import INTERFACE_MTU_MAX, INTERFACE_MTU_MIN
from dcim.forms import INTERFACE_MODE_HELP_TEXT
from dcim.models import Device, DeviceRole, Platform, Rack, Region, Site
from extras.forms import (
    AddRemoveTagsForm, CustomFieldBulkEditForm, CustomFieldModelCSVForm, CustomFieldModelForm, CustomFieldFilterForm,
)
from extras.models import Tag
from ipam.models import IPAddress, VLAN
from tenancy.forms import TenancyFilterForm, TenancyForm
from tenancy.models import Tenant
from utilities.forms import (
    add_blank_choice, APISelect, APISelectMultiple, BootstrapMixin, BulkEditForm, BulkEditNullBooleanSelect,
    CommentField, ConfirmationForm, CSVChoiceField, CSVModelChoiceField, CSVModelForm, DynamicModelChoiceField,
    DynamicModelMultipleChoiceField, ExpandableNameField, form_from_model, JSONField, SlugField, SmallTextarea,
    StaticSelect2, StaticSelect2Multiple, TagFilterField, BOOLEAN_WITH_BLANK_CHOICES,
)
from .choices import *
from .models import Cluster, ClusterGroup, ClusterType, Interface, VirtualMachine


#
# Cluster types
#

class ClusterTypeForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterType
        fields = [
            'name', 'slug', 'description',
        ]


class ClusterTypeCSVForm(CSVModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterType
        fields = ClusterType.csv_headers


#
# Cluster groups
#

class ClusterGroupForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterGroup
        fields = [
            'name', 'slug', 'description',
        ]


class ClusterGroupCSVForm(CSVModelForm):
    slug = SlugField()

    class Meta:
        model = ClusterGroup
        fields = ClusterGroup.csv_headers


#
# Clusters
#

class ClusterForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    type = DynamicModelChoiceField(
        queryset=ClusterType.objects.all()
    )
    group = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Cluster
        fields = (
            'name', 'type', 'group', 'tenant', 'site', 'comments', 'tags',
        )


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
        fields = Cluster.csv_headers


class ClusterBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    type = DynamicModelChoiceField(
        queryset=ClusterType.objects.all(),
        required=False
    )
    group = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Comments'
    )

    class Meta:
        nullable_fields = [
            'group', 'site', 'comments', 'tenant',
        ]


class ClusterFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldFilterForm):
    model = Cluster
    field_order = [
        'q', 'type', 'region', 'site', 'group', 'tenant_group', 'tenant'
    ]
    q = forms.CharField(required=False, label='Search')
    type = DynamicModelMultipleChoiceField(
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field='slug',
        )
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            filter_for={
                'site': 'region'
            }
        )
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field='slug',
            null_option=True,
        )
    )
    group = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field='slug',
            null_option=True,
        )
    )
    tag = TagFilterField(model)


class ClusterAddDevicesForm(BootstrapMixin, forms.Form):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        widget=APISelect(
            filter_for={
                "site": "region_id",
            },
            attrs={
                'nullable': 'true',
            }
        )
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        widget=APISelect(
            filter_for={
                "rack": "site_id",
                "devices": "site_id",
            }
        )
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        widget=APISelect(
            filter_for={
                "devices": "rack_id"
            },
            attrs={
                'nullable': 'true',
            }
        )
    )
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.filter(cluster__isnull=True),
        widget=APISelectMultiple(
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

class VirtualMachineForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    cluster_group = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        widget=APISelect(
            filter_for={
                "cluster": "group_id",
            },
            attrs={
                'nullable': 'true',
            }
        )
    )
    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all()
    )
    role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        widget=APISelect(
            additional_query_params={
                "vm_role": "True"
            }
        )
    )
    platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
        required=False
    )
    local_context_data = JSONField(
        required=False,
        label=''
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
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
            'primary_ip4': StaticSelect2(),
            'primary_ip6': StaticSelect2(),
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
                    address__family=family,
                    assigned_object_type=ContentType.objects.get_for_model(Interface),
                    assigned_object_id__in=self.instance.interfaces.values_list('id', flat=True)
                )
                if interface_ips:
                    ip_choices.append(
                        ('Interface IPs', [
                            (ip.id, '{} ({})'.format(ip.address, ip.interface)) for ip in interface_ips
                        ])
                    )
                # Collect NAT IPs
                nat_ips = IPAddress.objects.prefetch_related('nat_inside').filter(
                    address__family=family,
                    nat_inside__assigned_object_type=ContentType.objects.get_for_model(Interface),
                    nat_inside__assigned_object_id__in=self.instance.interfaces.values_list('id', flat=True)
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


class VirtualMachineCSVForm(CustomFieldModelCSVForm):
    status = CSVChoiceField(
        choices=VirtualMachineStatusChoices,
        required=False,
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
        fields = VirtualMachine.csv_headers


class VirtualMachineBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(VirtualMachineStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect2(),
    )
    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        required=False
    )
    role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.filter(
            vm_role=True
        ),
        required=False,
        widget=APISelect(
            additional_query_params={
                "vm_role": "True"
            }
        )
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    platform = DynamicModelChoiceField(
        queryset=Platform.objects.all(),
        required=False
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
        widget=SmallTextarea,
        label='Comments'
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
    cluster_group = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
        )
    )
    cluster_type = DynamicModelMultipleChoiceField(
        queryset=ClusterType.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
        )
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label='Cluster'
    )
    region = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            filter_for={
                'site': 'region'
            }
        )
    )
    site = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
        )
    )
    role = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.filter(vm_role=True),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
            additional_query_params={
                'vm_role': "True"
            }
        )
    )
    status = forms.MultipleChoiceField(
        choices=VirtualMachineStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    platform = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        to_field_name='slug',
        required=False,
        widget=APISelectMultiple(
            value_field="slug",
            null_option=True,
        )
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC address'
    )
    tag = TagFilterField(model)


#
# VM interfaces
#

class InterfaceForm(BootstrapMixin, forms.ModelForm):
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        widget=APISelect(
            display_field='display_name',
            full=True,
            additional_query_params={
                'site_id': 'null',
            },
        )
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        widget=APISelectMultiple(
            display_field='display_name',
            full=True,
            additional_query_params={
                'site_id': 'null',
            },
        )
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Interface
        fields = [
            'virtual_machine', 'name', 'enabled', 'mac_address', 'mtu', 'description', 'mode', 'tags', 'untagged_vlan',
            'tagged_vlans',
        ]
        widgets = {
            'virtual_machine': forms.HiddenInput(),
            'mode': StaticSelect2()
        }
        labels = {
            'mode': '802.1Q Mode',
        }
        help_texts = {
            'mode': INTERFACE_MODE_HELP_TEXT,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add current site to VLANs query params
        site = self.instance.virtual_machine.site
        if site is not None:
            # Add current site to VLANs query params
            self.fields['untagged_vlan'].widget.add_additional_query_param('site_id', site.pk)
            self.fields['tagged_vlans'].widget.add_additional_query_param('site_id', site.pk)

    def clean(self):
        super().clean()

        # Validate VLAN assignments
        tagged_vlans = self.cleaned_data['tagged_vlans']

        # Untagged interfaces cannot be assigned tagged VLANs
        if self.cleaned_data['mode'] == InterfaceModeChoices.MODE_ACCESS and tagged_vlans:
            raise forms.ValidationError({
                'mode': "An access interface cannot have tagged VLANs assigned."
            })

        # Remove all tagged VLAN assignments from "tagged all" interfaces
        elif self.cleaned_data['mode'] == InterfaceModeChoices.MODE_TAGGED_ALL:
            self.cleaned_data['tagged_vlans'] = []


class InterfaceCreateForm(BootstrapMixin, forms.Form):
    virtual_machine = forms.ModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        widget=forms.HiddenInput()
    )
    name_pattern = ExpandableNameField(
        label='Name'
    )
    enabled = forms.BooleanField(
        required=False,
        initial=True
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=INTERFACE_MTU_MIN,
        max_value=INTERFACE_MTU_MAX,
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
    mode = forms.ChoiceField(
        choices=add_blank_choice(InterfaceModeChoices),
        required=False,
        widget=StaticSelect2(),
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        widget=APISelect(
            display_field='display_name',
            full=True,
            additional_query_params={
                'site_id': 'null',
            },
        )
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        widget=APISelectMultiple(
            display_field='display_name',
            full=True,
            additional_query_params={
                'site_id': 'null',
            },
        )
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        virtual_machine = VirtualMachine.objects.get(
            pk=self.initial.get('virtual_machine') or self.data.get('virtual_machine')
        )

        site = getattr(virtual_machine.cluster, 'site', None)
        if site is not None:
            # Add current site to VLANs query params
            self.fields['untagged_vlan'].widget.add_additional_query_param('site_id', site.pk)
            self.fields['tagged_vlans'].widget.add_additional_query_param('site_id', site.pk)


class InterfaceBulkEditForm(BootstrapMixin, BulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Interface.objects.all(),
        widget=forms.MultipleHiddenInput()
    )
    virtual_machine = forms.ModelChoiceField(
        queryset=VirtualMachine.objects.all(),
        widget=forms.HiddenInput()
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=BulkEditNullBooleanSelect()
    )
    mtu = forms.IntegerField(
        required=False,
        min_value=INTERFACE_MTU_MIN,
        max_value=INTERFACE_MTU_MAX,
        label='MTU'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    mode = forms.ChoiceField(
        choices=add_blank_choice(InterfaceModeChoices),
        required=False,
        widget=StaticSelect2()
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        widget=APISelect(
            display_field='display_name',
            full=True,
            additional_query_params={
                'site_id': 'null',
            },
        )
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        widget=APISelectMultiple(
            display_field='display_name',
            full=True,
            additional_query_params={
                'site_id': 'null',
            },
        )
    )

    class Meta:
        nullable_fields = [
            'mtu', 'description',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Limit available VLANs based on the parent VirtualMachine
        if 'virtual_machine' in self.initial:
            parent_obj = VirtualMachine.objects.filter(pk=self.initial['virtual_machine']).first()

            site = getattr(parent_obj.cluster, 'site', None)
            if site is not None:
                # Add current site to VLANs query params
                self.fields['untagged_vlan'].widget.add_additional_query_param('site_id', site.pk)
                self.fields['tagged_vlans'].widget.add_additional_query_param('site_id', site.pk)


class InterfaceFilterForm(forms.Form):
    model = Interface
    enabled = forms.NullBooleanField(
        required=False,
        widget=StaticSelect2(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


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

    def clean_tags(self):
        # Because we're feeding TagField data (on the bulk edit form) to another TagField (on the model form), we
        # must first convert the list of tags to a string.
        return ','.join(self.cleaned_data.get('tags'))


class InterfaceBulkCreateForm(
    form_from_model(Interface, ['enabled', 'mtu', 'description', 'tags']),
    VirtualMachineBulkAddComponentForm
):
    pass
