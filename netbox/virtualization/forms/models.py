from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from dcim.forms.common import InterfaceCommonForm
from dcim.forms.models import INTERFACE_MODE_HELP_TEXT
from dcim.models import Device, DeviceRole, Platform, Rack, Region, Site, SiteGroup
from extras.forms import CustomFieldModelForm
from extras.models import Tag
from ipam.models import IPAddress, VLAN, VLANGroup
from tenancy.forms import TenancyForm
from utilities.forms import (
    BootstrapMixin, CommentField, ConfirmationForm, DynamicModelChoiceField, DynamicModelMultipleChoiceField,
    JSONField, SlugField, StaticSelect,
)
from virtualization.models import *

__all__ = (
    'ClusterAddDevicesForm',
    'ClusterForm',
    'ClusterGroupForm',
    'ClusterRemoveDevicesForm',
    'ClusterTypeForm',
    'VirtualMachineForm',
    'VMInterfaceForm',
)


class ClusterTypeForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = ClusterType
        fields = (
            'name', 'slug', 'description', 'tags',
        )


class ClusterGroupForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = ClusterGroup
        fields = (
            'name', 'slug', 'description', 'tags',
        )


class ClusterForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    type = DynamicModelChoiceField(
        queryset=ClusterType.objects.all()
    )
    group = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False
    )
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        initial_params={
            'sites': '$site'
        }
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Cluster
        fields = (
            'name', 'type', 'group', 'tenant', 'region', 'site_group', 'site', 'comments', 'tags',
        )
        fieldsets = (
            ('Cluster', ('name', 'type', 'group', 'region', 'site_group', 'site', 'tags')),
            ('Tenancy', ('tenant_group', 'tenant')),
        )


class ClusterAddDevicesForm(BootstrapMixin, forms.Form):
    region = DynamicModelChoiceField(
        queryset=Region.objects.all(),
        required=False,
        null_option='None'
    )
    site_group = DynamicModelChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        null_option='None'
    )
    site = DynamicModelChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        }
    )
    rack = DynamicModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'site_id': '$site'
        }
    )
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        query_params={
            'site_id': '$site',
            'rack_id': '$rack',
            'cluster_id': 'null',
        }
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


class VirtualMachineForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    cluster_group = DynamicModelChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        null_option='None',
        initial_params={
            'clusters': '$cluster'
        }
    )
    cluster = DynamicModelChoiceField(
        queryset=Cluster.objects.all(),
        query_params={
            'group_id': '$cluster_group'
        }
    )
    role = DynamicModelChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        query_params={
            "vm_role": "True"
        }
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
        fieldsets = (
            ('Virtual Machine', ('name', 'role', 'status', 'tags')),
            ('Cluster', ('cluster_group', 'cluster')),
            ('Tenancy', ('tenant_group', 'tenant')),
            ('Management', ('platform', 'primary_ip4', 'primary_ip6')),
            ('Resources', ('vcpus', 'memory', 'disk')),
            ('Config Context', ('local_context_data',)),
        )
        help_texts = {
            'local_context_data': "Local config context data overwrites all sources contexts in the final rendered "
                                  "config context",
        }
        widgets = {
            "status": StaticSelect(),
            'primary_ip4': StaticSelect(),
            'primary_ip6': StaticSelect(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:

            # Compile list of choices for primary IPv4 and IPv6 addresses
            for family in [4, 6]:
                ip_choices = [(None, '---------')]

                # Gather PKs of all interfaces belonging to this VM
                interface_ids = self.instance.interfaces.values_list('pk', flat=True)

                # Collect interface IPs
                interface_ips = IPAddress.objects.filter(
                    address__family=family,
                    assigned_object_type=ContentType.objects.get_for_model(VMInterface),
                    assigned_object_id__in=interface_ids
                )
                if interface_ips:
                    ip_list = [(ip.id, f'{ip.address} ({ip.assigned_object})') for ip in interface_ips]
                    ip_choices.append(('Interface IPs', ip_list))
                # Collect NAT IPs
                nat_ips = IPAddress.objects.prefetch_related('nat_inside').filter(
                    address__family=family,
                    nat_inside__assigned_object_type=ContentType.objects.get_for_model(VMInterface),
                    nat_inside__assigned_object_id__in=interface_ids
                )
                if nat_ips:
                    ip_list = [(ip.id, f'{ip.address} (NAT)') for ip in nat_ips]
                    ip_choices.append(('NAT IPs', ip_list))
                self.fields['primary_ip{}'.format(family)].choices = ip_choices

        else:

            # An object that doesn't exist yet can't have any IPs assigned to it
            self.fields['primary_ip4'].choices = []
            self.fields['primary_ip4'].widget.attrs['readonly'] = True
            self.fields['primary_ip6'].choices = []
            self.fields['primary_ip6'].widget.attrs['readonly'] = True


class VMInterfaceForm(BootstrapMixin, InterfaceCommonForm, CustomFieldModelForm):
    parent = DynamicModelChoiceField(
        queryset=VMInterface.objects.all(),
        required=False,
        label='Parent interface'
    )
    vlan_group = DynamicModelChoiceField(
        queryset=VLANGroup.objects.all(),
        required=False,
        label='VLAN group'
    )
    untagged_vlan = DynamicModelChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='Untagged VLAN',
        query_params={
            'group_id': '$vlan_group',
        }
    )
    tagged_vlans = DynamicModelMultipleChoiceField(
        queryset=VLAN.objects.all(),
        required=False,
        label='Tagged VLANs',
        query_params={
            'group_id': '$vlan_group',
        }
    )
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = VMInterface
        fields = [
            'virtual_machine', 'name', 'enabled', 'parent', 'mac_address', 'mtu', 'description', 'mode', 'tags',
            'untagged_vlan', 'tagged_vlans',
        ]
        widgets = {
            'virtual_machine': forms.HiddenInput(),
            'mode': StaticSelect()
        }
        labels = {
            'mode': '802.1Q Mode',
        }
        help_texts = {
            'mode': INTERFACE_MODE_HELP_TEXT,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        vm_id = self.initial.get('virtual_machine') or self.data.get('virtual_machine')

        # Restrict parent interface assignment by VM
        self.fields['parent'].widget.add_query_param('virtual_machine_id', vm_id)

        # Limit VLAN choices by virtual machine
        self.fields['untagged_vlan'].widget.add_query_param('available_on_virtualmachine', vm_id)
        self.fields['tagged_vlans'].widget.add_query_param('available_on_virtualmachine', vm_id)
