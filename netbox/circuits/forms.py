from django import forms
from django.db.models import Count

from dcim.models import Site, Device, Interface, Rack, IFACE_FF_VIRTUAL
from extras.forms import CustomFieldForm, CustomFieldBulkEditForm, CustomFieldFilterForm
from tenancy.models import Tenant
from utilities.forms import (
    APISelect, BootstrapMixin, BulkImportForm, CommentField, CSVDataField, FilterChoiceField, Livesearch, SmallTextarea,
    SlugField,
)

from .models import Circuit, CircuitTermination, CircuitType, Provider


#
# Providers
#

class ProviderForm(BootstrapMixin, CustomFieldForm):
    slug = SlugField()
    comments = CommentField()

    class Meta:
        model = Provider
        fields = ['name', 'slug', 'asn', 'account', 'portal_url', 'noc_contact', 'admin_contact', 'comments']
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


class ProviderFromCSVForm(forms.ModelForm):

    class Meta:
        model = Provider
        fields = ['name', 'slug', 'asn', 'account', 'portal_url']


class ProviderImportForm(BootstrapMixin, BulkImportForm):
    csv = CSVDataField(csv_form=ProviderFromCSVForm)


class ProviderBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
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


#
# Circuit types
#

class CircuitTypeForm(BootstrapMixin, forms.ModelForm):
    slug = SlugField()

    class Meta:
        model = CircuitType
        fields = ['name', 'slug']


#
# Circuits
#

class CircuitForm(BootstrapMixin, CustomFieldForm):
    comments = CommentField()

    class Meta:
        model = Circuit
        fields = ['cid', 'type', 'provider', 'tenant', 'install_date', 'commit_rate', 'description', 'comments']
        help_texts = {
            'cid': "Unique circuit ID",
            'install_date': "Format: YYYY-MM-DD",
            'commit_rate': "Committed rate",
        }


class CircuitFromCSVForm(forms.ModelForm):
    provider = forms.ModelChoiceField(Provider.objects.all(), to_field_name='name',
                                      error_messages={'invalid_choice': 'Provider not found.'})
    type = forms.ModelChoiceField(CircuitType.objects.all(), to_field_name='name',
                                  error_messages={'invalid_choice': 'Invalid circuit type.'})
    tenant = forms.ModelChoiceField(Tenant.objects.all(), to_field_name='name', required=False,
                                    error_messages={'invalid_choice': 'Tenant not found.'})

    class Meta:
        model = Circuit
        fields = ['cid', 'provider', 'type', 'tenant', 'install_date', 'commit_rate', 'description']


class CircuitImportForm(BootstrapMixin, BulkImportForm):
    csv = CSVDataField(csv_form=CircuitFromCSVForm)


class CircuitBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Circuit.objects.all(), widget=forms.MultipleHiddenInput)
    type = forms.ModelChoiceField(queryset=CircuitType.objects.all(), required=False)
    provider = forms.ModelChoiceField(queryset=Provider.objects.all(), required=False)
    tenant = forms.ModelChoiceField(queryset=Tenant.objects.all(), required=False)
    commit_rate = forms.IntegerField(required=False, label='Commit rate (Kbps)')
    description = forms.CharField(max_length=100, required=False)
    comments = CommentField(widget=SmallTextarea)

    class Meta:
        nullable_fields = ['tenant', 'commit_rate', 'description', 'comments']


class CircuitFilterForm(BootstrapMixin, CustomFieldFilterForm):
    model = Circuit
    q = forms.CharField(required=False, label='Search')
    type = FilterChoiceField(queryset=CircuitType.objects.annotate(filter_count=Count('circuits')),
                             to_field_name='slug')
    provider = FilterChoiceField(queryset=Provider.objects.annotate(filter_count=Count('circuits')),
                                 to_field_name='slug')
    tenant = FilterChoiceField(queryset=Tenant.objects.annotate(filter_count=Count('circuits')), to_field_name='slug',
                               null_option=(0, 'None'))
    site = FilterChoiceField(queryset=Site.objects.annotate(filter_count=Count('circuit_terminations')),
                             to_field_name='slug')


#
# Circuit terminations
#

class CircuitTerminationForm(BootstrapMixin, forms.ModelForm):
    site = forms.ModelChoiceField(
        queryset=Site.objects.all(),
        widget=forms.Select(
            attrs={'filter-for': 'rack'}
        )
    )
    rack = forms.ModelChoiceField(
        queryset=Rack.objects.all(),
        required=False,
        label='Rack',
        widget=APISelect(
            api_url='/api/dcim/racks/?site_id={{site}}',
            attrs={'filter-for': 'device', 'nullable': 'true'}
        )
    )
    device = forms.ModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Device',
        widget=APISelect(
            api_url='/api/dcim/devices/?site_id={{site}}&rack_id={{rack}}',
            display_field='display_name',
            attrs={'filter-for': 'interface'}
        )
    )
    livesearch = forms.CharField(
        required=False,
        label='Device',
        widget=Livesearch(
            query_key='q',
            query_url='dcim-api:device_list',
            field_to_update='device'
        )
    )
    interface = forms.ModelChoiceField(
        queryset=Interface.objects.all(),
        required=False,
        label='Interface',
        widget=APISelect(
            api_url='/api/dcim/devices/{{device}}/interfaces/?type=physical',
            disabled_indicator='is_connected'
        )
    )

    class Meta:
        model = CircuitTermination
        fields = ['term_side', 'site', 'rack', 'device', 'livesearch', 'interface', 'port_speed', 'upstream_speed',
                  'xconnect_id', 'pp_info']
        help_texts = {
            'port_speed': "Physical circuit speed",
            'xconnect_id': "ID of the local cross-connect",
            'pp_info': "Patch panel ID and port number(s)"
        }
        widgets = {
            'term_side': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):

        super(CircuitTerminationForm, self).__init__(*args, **kwargs)

        # If an interface has been assigned, initialize rack and device
        if self.instance.interface:
            self.initial['rack'] = self.instance.interface.device.rack
            self.initial['device'] = self.instance.interface.device

        # Limit rack choices
        if self.is_bound:
            self.fields['rack'].queryset = Rack.objects.filter(site__pk=self.data['site'])
        elif self.initial.get('site'):
            self.fields['rack'].queryset = Rack.objects.filter(site=self.initial['site'])
        else:
            self.fields['rack'].choices = []

        # Limit device choices
        if self.is_bound and self.data.get('rack'):
            self.fields['device'].queryset = Device.objects.filter(rack=self.data['rack'])
        elif self.initial.get('rack'):
            self.fields['device'].queryset = Device.objects.filter(rack=self.initial['rack'])
        else:
            self.fields['device'].choices = []

        # Limit interface choices
        if self.is_bound and self.data.get('device'):
            interfaces = Interface.objects.filter(device=self.data['device'])\
                .exclude(form_factor=IFACE_FF_VIRTUAL).select_related('circuit_termination', 'connected_as_a',
                                                                      'connected_as_b')
            self.fields['interface'].widget.attrs['initial'] = self.data.get('interface')
        elif self.initial.get('device'):
            interfaces = Interface.objects.filter(device=self.initial['device'])\
                .exclude(form_factor=IFACE_FF_VIRTUAL).select_related('circuit_termination', 'connected_as_a',
                                                                      'connected_as_b')
            self.fields['interface'].widget.attrs['initial'] = self.initial.get('interface')
        else:
            interfaces = []
        self.fields['interface'].choices = [
            (iface.id, {
                'label': iface.name,
                'disabled': iface.is_connected and iface.id != self.fields['interface'].widget.attrs.get('initial'),
            }) for iface in interfaces
        ]
