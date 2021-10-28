from django import forms
from django.utils.translation import gettext as _

from dcim.models import DeviceRole, Platform, Region, Site, SiteGroup
from extras.forms import CustomFieldModelFilterForm, LocalConfigContextFilterForm
from tenancy.forms import TenancyFilterForm
from utilities.forms import (
    BootstrapMixin, DynamicModelMultipleChoiceField, StaticSelect, StaticSelectMultiple, TagFilterField,
    BOOLEAN_WITH_BLANK_CHOICES,
)
from virtualization.choices import *
from virtualization.models import *

__all__ = (
    'ClusterFilterForm',
    'ClusterGroupFilterForm',
    'ClusterTypeFilterForm',
    'VirtualMachineFilterForm',
    'VMInterfaceFilterForm',
)


class ClusterTypeFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = ClusterType
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    tag = TagFilterField(model)


class ClusterGroupFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = ClusterGroup
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    tag = TagFilterField(model)


class ClusterFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldModelFilterForm):
    model = Cluster
    field_order = [
        'q', 'type_id', 'region_id', 'site_id', 'group_id', 'tenant_group_id', 'tenant_id',
    ]
    field_groups = [
        ['q', 'tag'],
        ['group_id', 'type_id'],
        ['region_id', 'site_group_id', 'site_id'],
        ['tenant_group_id', 'tenant_id'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    type_id = DynamicModelMultipleChoiceField(
        queryset=ClusterType.objects.all(),
        required=False,
        label=_('Type'),
        fetch_trigger='open'
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region_id': '$region_id',
            'site_group_id': '$site_group_id',
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Group'),
        fetch_trigger='open'
    )
    tag = TagFilterField(model)


class VirtualMachineFilterForm(
    BootstrapMixin,
    LocalConfigContextFilterForm,
    TenancyFilterForm,
    CustomFieldModelFilterForm
):
    model = VirtualMachine
    field_groups = [
        ['q', 'tag'],
        ['cluster_group_id', 'cluster_type_id', 'cluster_id'],
        ['region_id', 'site_group_id', 'site_id'],
        ['status', 'role_id', 'platform_id', 'mac_address', 'has_primary_ip', 'local_context_data'],
        ['tenant_group_id', 'tenant_id'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    cluster_group_id = DynamicModelMultipleChoiceField(
        queryset=ClusterGroup.objects.all(),
        required=False,
        null_option='None',
        label=_('Cluster group'),
        fetch_trigger='open'
    )
    cluster_type_id = DynamicModelMultipleChoiceField(
        queryset=ClusterType.objects.all(),
        required=False,
        null_option='None',
        label=_('Cluster type'),
        fetch_trigger='open'
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label=_('Cluster'),
        fetch_trigger='open'
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region'),
        fetch_trigger='open'
    )
    site_group_id = DynamicModelMultipleChoiceField(
        queryset=SiteGroup.objects.all(),
        required=False,
        label=_('Site group'),
        fetch_trigger='open'
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'region_id': '$region_id',
            'group_id': '$site_group_id',
        },
        label=_('Site'),
        fetch_trigger='open'
    )
    role_id = DynamicModelMultipleChoiceField(
        queryset=DeviceRole.objects.all(),
        required=False,
        null_option='None',
        query_params={
            'vm_role': "True"
        },
        label=_('Role'),
        fetch_trigger='open'
    )
    status = forms.MultipleChoiceField(
        choices=VirtualMachineStatusChoices,
        required=False,
        widget=StaticSelectMultiple()
    )
    platform_id = DynamicModelMultipleChoiceField(
        queryset=Platform.objects.all(),
        required=False,
        null_option='None',
        label=_('Platform'),
        fetch_trigger='open'
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC address'
    )
    has_primary_ip = forms.NullBooleanField(
        required=False,
        label='Has a primary IP',
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    tag = TagFilterField(model)


class VMInterfaceFilterForm(BootstrapMixin, forms.Form):
    model = VMInterface
    field_groups = [
        ['q', 'tag'],
        ['cluster_id', 'virtual_machine_id'],
        ['enabled', 'mac_address'],
    ]
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': _('All Fields')}),
        label=_('Search')
    )
    cluster_id = DynamicModelMultipleChoiceField(
        queryset=Cluster.objects.all(),
        required=False,
        label=_('Cluster'),
        fetch_trigger='open'
    )
    virtual_machine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        query_params={
            'cluster_id': '$cluster_id'
        },
        label=_('Virtual machine'),
        fetch_trigger='open'
    )
    enabled = forms.NullBooleanField(
        required=False,
        widget=StaticSelect(
            choices=BOOLEAN_WITH_BLANK_CHOICES
        )
    )
    mac_address = forms.CharField(
        required=False,
        label='MAC address'
    )
    tag = TagFilterField(model)
