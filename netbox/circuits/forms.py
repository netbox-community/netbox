from django import forms
from django.utils.translation import gettext as _

from dcim.models import Region, Site, SiteGroup
from extras.forms import (
    AddRemoveTagsForm, CustomFieldModelBulkEditForm, CustomFieldModelFilterForm, CustomFieldModelForm, CustomFieldModelCSVForm,
)
from extras.models import Tag
from tenancy.forms import TenancyFilterForm, TenancyForm
from tenancy.models import Tenant
from utilities.forms import (
    add_blank_choice, BootstrapMixin, CommentField, CSVChoiceField, CSVModelChoiceField, DatePicker,
    DynamicModelChoiceField, DynamicModelMultipleChoiceField, SelectSpeedWidget, SmallTextarea, SlugField,
    StaticSelect2, StaticSelect2Multiple, TagFilterField,
)
from .choices import CircuitStatusChoices
from .models import *


#
# Providers
#

class ProviderForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Provider
        fields = [
            'name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments', 'tags',
        ]
        fieldsets = (
            ('Provider', ('name', 'slug', 'asn', 'tags')),
            ('Support Info', ('account', 'portal_url', 'noc_contact', 'admin_contact')),
        )
        widgets = {
            'noc_contact': SmallTextarea(
                attrs={'rows': 5}
            ),
            'admin_contact': SmallTextarea(
                attrs={'rows': 5}
            ),
        }
        help_texts = {
            'name': "Full name of the provider",
            'asn': "BGP autonomous system number (if applicable)",
            'portal_url': "URL of the provider's customer support portal",
            'noc_contact': "NOC email address and phone number",
            'admin_contact': "Administrative contact email address and phone number",
        }


class ProviderCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = Provider
        fields = (
            'name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments',
        )


class ProviderBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    asn = forms.IntegerField(
        required=False,
        label='ASN'
    )
    account = forms.CharField(
        max_length=30,
        required=False,
        label='Account number'
    )
    portal_url = forms.URLField(
        required=False,
        label='Portal'
    )
    noc_contact = forms.CharField(
        required=False,
        widget=SmallTextarea,
        label='NOC contact'
    )
    admin_contact = forms.CharField(
        required=False,
        widget=SmallTextarea,
        label='Admin contact'
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Comments'
    )

    class Meta:
        nullable_fields = [
            'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments',
        ]


class ProviderFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = Provider
    field_groups = [
        ['region_id', 'site_id'],
        ['asn', 'tag'],
    ]
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site')
    )
    asn = forms.IntegerField(
        required=False,
        label=_('ASN')
    )
    tag = TagFilterField(model)


#
# Provider networks
#

class ProviderNetworkForm(BootstrapMixin, CustomFieldModelForm):
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all()
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = ProviderNetwork
        fields = [
            'provider', 'name', 'description', 'comments', 'tags',
        ]
        fieldsets = (
            ('Provider Network', ('provider', 'name', 'description', 'tags')),
        )


class ProviderNetworkCSVForm(CustomFieldModelCSVForm):
    provider = CSVModelChoiceField(
        queryset=Provider.objects.all(),
        to_field_name='name',
        help_text='Assigned provider'
    )

    class Meta:
        model = ProviderNetwork
        fields = [
            'provider', 'name', 'description', 'comments',
        ]


class ProviderNetworkBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=ProviderNetwork.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=False
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Comments'
    )

    class Meta:
        nullable_fields = [
            'description', 'comments',
        ]


class ProviderNetworkFilterForm(BootstrapMixin, CustomFieldModelFilterForm):
    model = ProviderNetwork
    field_order = ['provider_id']
    provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label=_('Provider')
    )
    tag = TagFilterField(model)


#
# Circuit types
#

class CircuitTypeForm(BootstrapMixin, CustomFieldModelForm):
    slug = SlugField()

    class Meta:
        model = CircuitType
        fields = [
            'name', 'slug', 'description',
        ]


class CircuitTypeBulkEditForm(BootstrapMixin, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=CircuitType.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    description = forms.CharField(
        max_length=200,
        required=False
    )

    class Meta:
        nullable_fields = ['description']


class CircuitTypeCSVForm(CustomFieldModelCSVForm):
    slug = SlugField()

    class Meta:
        model = CircuitType
        fields = ('name', 'slug', 'description')
        help_texts = {
            'name': 'Name of circuit type',
        }


#
# Circuits
#

class CircuitForm(BootstrapMixin, TenancyForm, CustomFieldModelForm):
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all()
    )
    type = DynamicModelChoiceField(
        queryset=CircuitType.objects.all()
    )
    comments = CommentField()
    tags = DynamicModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False
    )

    class Meta:
        model = Circuit
        fields = [
            'cid', 'type', 'provider', 'status', 'install_date', 'commit_rate', 'description', 'tenant_group', 'tenant',
            'comments', 'tags',
        ]
        fieldsets = (
            ('Circuit', ('provider', 'cid', 'type', 'status', 'install_date', 'commit_rate', 'description', 'tags')),
            ('Tenancy', ('tenant_group', 'tenant')),
        )
        help_texts = {
            'cid': "Unique circuit ID",
            'commit_rate': "Committed rate",
        }
        widgets = {
            'status': StaticSelect2(),
            'install_date': DatePicker(),
            'commit_rate': SelectSpeedWidget(),
        }


class CircuitCSVForm(CustomFieldModelCSVForm):
    provider = CSVModelChoiceField(
        queryset=Provider.objects.all(),
        to_field_name='name',
        help_text='Assigned provider'
    )
    type = CSVModelChoiceField(
        queryset=CircuitType.objects.all(),
        to_field_name='name',
        help_text='Type of circuit'
    )
    status = CSVChoiceField(
        choices=CircuitStatusChoices,
        required=False,
        help_text='Operational status'
    )
    tenant = CSVModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        to_field_name='name',
        help_text='Assigned tenant'
    )

    class Meta:
        model = Circuit
        fields = [
            'cid', 'provider', 'type', 'status', 'tenant', 'install_date', 'commit_rate', 'description', 'comments',
        ]


class CircuitBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldModelBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Circuit.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    type = DynamicModelChoiceField(
        queryset=CircuitType.objects.all(),
        required=False
    )
    provider = DynamicModelChoiceField(
        queryset=Provider.objects.all(),
        required=False
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(CircuitStatusChoices),
        required=False,
        initial='',
        widget=StaticSelect2()
    )
    tenant = DynamicModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False
    )
    commit_rate = forms.IntegerField(
        required=False,
        label='Commit rate (Kbps)'
    )
    description = forms.CharField(
        max_length=100,
        required=False
    )
    comments = CommentField(
        widget=SmallTextarea,
        label='Comments'
    )

    class Meta:
        nullable_fields = [
            'tenant', 'commit_rate', 'description', 'comments',
        ]


class CircuitFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldModelFilterForm):
    model = Circuit
    field_order = [
        'type_id', 'provider_id', 'provider_network_id', 'status', 'region_id', 'site_id', 'tenant_group_id', 'tenant_id',
        'commit_rate',
    ]
    field_groups = [
        ['type_id', 'status', 'commit_rate'],
        ['provider_id', 'provider_network_id'],
        ['region_id', 'site_id'],
        ['tenant_group_id', 'tenant_id'],
        ['tag']
    ]
    type_id = DynamicModelMultipleChoiceField(
        queryset=CircuitType.objects.all(),
        required=False,
        label=_('Type')
    )
    provider_id = DynamicModelMultipleChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        label=_('Provider')
    )
    provider_network_id = DynamicModelMultipleChoiceField(
        queryset=ProviderNetwork.objects.all(),
        required=False,
        query_params={
            'provider_id': '$provider_id'
        },
        label=_('Provider network')
    )
    status = forms.MultipleChoiceField(
        choices=CircuitStatusChoices,
        required=False,
        widget=StaticSelect2Multiple()
    )
    region_id = DynamicModelMultipleChoiceField(
        queryset=Region.objects.all(),
        required=False,
        label=_('Region')
    )
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        query_params={
            'region_id': '$region_id'
        },
        label=_('Site')
    )
    commit_rate = forms.IntegerField(
        required=False,
        min_value=0,
        label=_('Commit rate (Kbps)')
    )
    tag = TagFilterField(model)


#
# Circuit terminations
#

class CircuitTerminationForm(BootstrapMixin, forms.ModelForm):
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
        query_params={
            'region_id': '$region',
            'group_id': '$site_group',
        },
        required=False
    )
    provider_network = DynamicModelChoiceField(
        queryset=ProviderNetwork.objects.all(),
        required=False
    )

    class Meta:
        model = CircuitTermination
        fields = [
            'term_side', 'region', 'site_group', 'site', 'provider_network', 'mark_connected', 'port_speed',
            'upstream_speed', 'xconnect_id', 'pp_info', 'description',
        ]
        help_texts = {
            'port_speed': "Physical circuit speed",
            'xconnect_id': "ID of the local cross-connect",
            'pp_info': "Patch panel ID and port number(s)"
        }
        widgets = {
            'term_side': forms.HiddenInput(),
            'port_speed': SelectSpeedWidget(),
            'upstream_speed': SelectSpeedWidget(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['provider_network'].widget.add_query_param('provider_id', self.instance.circuit.provider_id)
