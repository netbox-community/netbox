from __future__ import unicode_literals

from django import forms
from django.db.models import Count
from taggit.forms import TagField

from dcim.models import Site, Device, Interface, Rack
from extras.forms import AddRemoveTagsForm, CustomFieldForm, CustomFieldBulkEditForm, CustomFieldFilterForm
from tenancy.forms import TenancyForm
from tenancy.models import Tenant
from utilities.forms import (
    AnnotatedMultipleChoiceField, APISelect, add_blank_choice, BootstrapMixin, ChainedFieldsMixin,
    ChainedModelChoiceField, CommentField, CSVChoiceField, FilterChoiceField, SmallTextarea, SlugField,
)
from .constants import CIRCUIT_STATUS_CHOICES
from .models import Circuit, CircuitTermination, CircuitType, Provider


#
# Providers
#

class ProviderForm(BootstrapMixin, CustomFieldForm):
    slug = SlugField()
    comments = CommentField()
    tags = TagField(required=False)

    class Meta:
        model = Provider
        fields = ['name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments', 'tags']
        widgets = {
            'noc_contact': SmallTextarea(attrs={'rows': 5}),
            'admin_contact': SmallTextarea(attrs={'rows': 5}),
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
    pk = forms.ModelMultipleChoiceField(queryset=Provider.objects.all(), widget=forms.MultipleHiddenInput)
    asn = forms.IntegerField(required=False, label='ASN')
    account = forms.CharField(max_length=30, required=False, label='Account number')
    portal_url = forms.URLField(required=False, label='Portal')
    noc_contact = forms.CharField(required=False, widget=SmallTextarea, label='NOC contact')
    admin_contact = forms.CharField(required=False, widget=SmallTextarea, label='Admin contact')
    comments = CommentField(widget=SmallTextarea)

    class Meta:
        nullable_fields = ['asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments']


class ProviderFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Provider
    q = forms.CharField(required=False, label='Search')
    site = FilterChoiceField(queryset=Site.objects.all(), to_field_name='slug')
    asn = forms.IntegerField(required=False, label='ASN')


#
# Circuit types
#

class CircuitTypeForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = CircuitType
        fields = ['name', 'slug']


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
    tags = TagField(required=False)

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
    pk = forms.ModelMultipleChoiceField(queryset=Circuit.objects.all(), widget=forms.MultipleHiddenInput)
    type = forms.ModelChoiceField(queryset=CircuitType.objects.all(), required=False)
    provider = forms.ModelChoiceField(queryset=Provider.objects.all(), required=False)
    status = forms.ChoiceField(choices=add_blank_choice(CIRCUIT_STATUS_CHOICES), required=False, initial='')
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False)
    commit_rate = forms.IntegerField(required=False, label='Commit rate (Kbps)')
    description = forms.CharField(max_length=100, required=False)
    comments = CommentField(widget=SmallTextarea)

    class Meta:
        nullable_fields = ['tenant', 'commit_rate', 'description', 'comments']


class CircuitFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Circuit
    q = forms.CharField(required=False, label='Search')
    type = FilterChoiceField(
        queryset=CircuitType.objects.annotate(filter_count=Count('circuits')),
        to_field_name='slug'
    )
    provider = FilterChoiceField(
        queryset=Provider.objects.annotate(filter_count=Count('circuits')),
        to_field_name='slug'
    )
    status = AnnotatedMultipleChoiceField(
        choices=CIRCUIT_STATUS_CHOICES,
        annotate=Circuit.objects.all(),
        annotate_field='status',
        required=False
    )
    tenant = FilterChoiceField(
        queryset=Tenant.objects.annotate(filter_count=Count('circuits')),
        to_field_name='slug',
        null_label='-- None --'
    )
    site = FilterChoiceField(
        queryset=Site.objects.annotate(filter_count=Count('circuit_terminations')),
        to_field_name='slug'
    )
    commit_rate = forms.IntegerField(required=False, min_value=0, label='Commit rate (Kbps)')


#
# Circuit terminations
#

class CircuitTerminationForm(BootstrapMixin, ChainedFieldsMixin, forms.ModelForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        widget=forms.Select(
            attrs={'filter-for': 'rack'}
        )
    )
    rack = ChainedModelChoiceField(
        queryset=Rack.objects.all(),
        chains=(
            ('site', 'site'),
        ),
        required=False,
        label='Rack',
        widget=APISelect(
            api_url='/api/dcim/racks/?site_id={{site}}',
            attrs={'filter-for': 'device', 'nullable': 'true'}
        )
    )
    device = ChainedModelChoiceField(
        queryset=Device.objects.all(),
        chains=(
            ('site', 'site'),
            ('rack', 'rack'),
        ),
        required=False,
        label='Device',
        widget=APISelect(
            api_url='/api/dcim/devices/?site_id={{site}}&rack_id={{rack}}',
            display_field='display_name',
            attrs={'filter-for': 'interface'}
        )
    )
    interface = ChainedModelChoiceField(
        queryset=Interface.objects.connectable().select_related(
            'circuit_termination', 'connected_as_a', 'connected_as_b'
        ),
        chains=(
            ('device', 'device'),
        ),
        required=False,
        label='Interface',
        widget=APISelect(
            api_url='/api/dcim/interfaces/?device_id={{device}}&type=physical',
            disabled_indicator='is_connected'
        )
    )

    class Meta:
        model = CircuitTermination
        fields = [
            'term_side', 'site', 'rack', 'device', 'interface', 'port_speed', 'upstream_speed', 'xconnect_id',
            'pp_info',
        ]
        help_texts = {
            'port_speed': "Physical circuit speed",
            'xconnect_id': "ID of the local cross-connect",
            'pp_info': "Patch panel ID and port number(s)"
        }
        widgets = {
            'term_side': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):

        # Initialize helper selectors
        instance = kwargs.get('instance')
        if instance and instance.interface is not None:
            initial = kwargs.get('initial', {}).copy()
            initial['rack'] = instance.interface.device.rack
            initial['device'] = instance.interface.device
            kwargs['initial'] = initial

        super(CircuitTerminationForm, self).__init__(*args, **kwargs)

        # Mark connected interfaces as disabled
        self.fields['interface'].choices = []
        for iface in self.fields['interface'].queryset:
            self.fields['interface'].choices.append(
                (iface.id, {
                    'label': iface.name,
                    'disabled': iface.is_connected and iface.pk != self.initial.get('interface'),
                })
            )
