from django import forms
from taggit.forms import TagField

from dcim.models import Site
from extras.forms import AddRemoveTagsForm, CustomFieldForm, CustomFieldBulkEditForm, CustomFieldFilterForm
from tenancy.forms import TenancyForm
from tenancy.forms import TenancyFilterForm
from tenancy.models import Tenant
from utilities.forms import (
    APISelect, APISelectMultiple, add_blank_choice, BootstrapMixin, CommentField, CSVChoiceField,
    FilterChoiceField, SmallTextarea, SlugField, StaticSelect2, StaticSelect2Multiple
)
from .constants import CIRCUIT_STATUS_CHOICES
from .models import Circuit, CircuitTermination, CircuitType, Provider


#
# Providers
#

class ProviderForm(BootstrapMixin, CustomFieldForm):
    slug = SlugField()
    comments = CommentField()
    tags = TagField(
        required=False
    )

    class Meta:
        model = Provider
        fields = [
            'name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments', 'tags',
        ]
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


class ProviderCSVForm(forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = Provider
        fields = Provider.csv_headers
        help_texts = {
            'name': 'Provider name',
            'asn': '32-bit autonomous system number',
            'portal_url': 'Portal URL',
            'comments': 'Free-form comments',
        }


class ProviderBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
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
        widget=SmallTextarea()
    )

    class Meta:
        nullable_fields = [
            'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments',
        ]


class ProviderFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Provider
    q = forms.CharField(
        required=False,
        label='Search'
    )
    site = FilterChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        widget=APISelectMultiple(
            api_url="/api/dcim/sites/",
            value_field="slug",
        )
    )
    asn = forms.IntegerField(
        required=False,
        label='ASN'
    )


#
# Circuit types
#

class CircuitTypeForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = CircuitType
        fields = [
            'name', 'slug',
        ]


class CircuitTypeCSVForm(forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = CircuitType
        fields = CircuitType.csv_headers
        help_texts = {
            'name': 'Name of circuit type',
        }


#
# Circuits
#

class CircuitForm(BootstrapMixin, TenancyForm, CustomFieldForm):
    comments = CommentField()
    tags = TagField(
        required=False
    )

    class Meta:
        model = Circuit
        fields = [
            'cid', 'type', 'provider', 'status', 'install_date', 'commit_rate', 'description', 'tenant_group', 'tenant',
            'comments', 'tags',
        ]
        help_texts = {
            'cid': "Unique circuit ID",
            'install_date': "Format: YYYY-MM-DD",
            'commit_rate': "Committed rate",
        }
        widgets = {
            'provider': APISelect(
                api_url="/api/circuits/providers/"
            ),
            'type': APISelect(
                api_url="/api/circuits/circuit-types/"
            ),
            'status': StaticSelect2(),

        }


class CircuitCSVForm(forms.ModelForm):
    provider = forms.ModelChoiceField(
        queryset=Provider.objects.all(),
        to_field_name='name',
        help_text='Name of parent provider',
        error_messages={
            'invalid_choice': 'Provider not found.'
        }
    )
    type = forms.ModelChoiceField(
        queryset=CircuitType.objects.all(),
        to_field_name='name',
        help_text='Type of circuit',
        error_messages={
            'invalid_choice': 'Invalid circuit type.'
        }
    )
    status = CSVChoiceField(
        choices=CIRCUIT_STATUS_CHOICES,
        required=False,
        help_text='Operational status'
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

    class Meta:
        model = Circuit
        fields = [
            'cid', 'provider', 'type', 'status', 'tenant', 'install_date', 'commit_rate', 'description', 'comments',
        ]


class CircuitBulkEditForm(BootstrapMixin, AddRemoveTagsForm, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(
        queryset=Circuit.objects.all(),
        widget=forms.MultipleHiddenInput
    )
    type = forms.ModelChoiceField(
        queryset=CircuitType.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/circuits/circuit-types/"
        )
    )
    provider = forms.ModelChoiceField(
        queryset=Provider.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/circuits/providers/"
        )
    )
    status = forms.ChoiceField(
        choices=add_blank_choice(CIRCUIT_STATUS_CHOICES),
        required=False,
        initial='',
        widget=StaticSelect2()
    )
    tenant = forms.ModelChoiceField(
        queryset=Tenant.objects.all(),
        required=False,
        widget=APISelect(
            api_url="/api/tenancy/tenants/"
        )
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
        widget=SmallTextarea
    )

    class Meta:
        nullable_fields = [
            'tenant', 'commit_rate', 'description', 'comments',
        ]


class CircuitFilterForm(BootstrapMixin, TenancyFilterForm, CustomFieldFilterForm):
    model = Circuit
    field_order = ['q', 'type', 'provider', 'status', 'site', 'tenant_group', 'tenant', 'commit_rate']
    q = forms.CharField(
        required=False,
        label='Search'
    )
    type = FilterChoiceField(
        queryset=CircuitType.objects.all(),
        to_field_name='slug',
        widget=APISelectMultiple(
            api_url="/api/circuits/circuit-types/",
            value_field="slug",
        )
    )
    provider = FilterChoiceField(
        queryset=Provider.objects.all(),
        to_field_name='slug',
        widget=APISelectMultiple(
            api_url="/api/circuits/providers/",
            value_field="slug",
        )
    )
    status = forms.MultipleChoiceField(
        choices=CIRCUIT_STATUS_CHOICES,
        required=False,
        widget=StaticSelect2Multiple()
    )
    site = FilterChoiceField(
        queryset=Site.objects.all(),
        to_field_name='slug',
        widget=APISelectMultiple(
            api_url="/api/dcim/sites/",
            value_field="slug",
        )
    )
    commit_rate = forms.IntegerField(
        required=False,
        min_value=0,
        label='Commit rate (Kbps)'
    )


#
# Circuit terminations
#

class CircuitTerminationForm(BootstrapMixin, forms.ModelForm):

    class Meta:
        model = CircuitTermination
        fields = [
            'term_side', 'site', 'port_speed', 'upstream_speed', 'xconnect_id', 'pp_info', 'description',
        ]
        help_texts = {
            'port_speed': "Physical circuit speed",
            'xconnect_id': "ID of the local cross-connect",
            'pp_info': "Patch panel ID and port number(s)"
        }
        widgets = {
            'term_side': forms.HiddenInput(),
            'site': APISelect(
                api_url="/api/dcim/sites/"
            )
        }
