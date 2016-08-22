from django import forms
from django.db.models import Count

from dcim.models import Site, Device, Interface, Rack, IFACE_FF_VIRTUAL
from extras.forms import CustomFieldForm, CustomFieldBulkEditForm
from tenancy.forms import bulkedit_tenant_choices
from tenancy.models import Tenant
from utilities.forms import (
    APISelect, BootstrapMixin, BulkImportForm, CommentField, CSVDataField, Livesearch, SmallTextarea, SlugField,
)

from .models import Circuit, CircuitType, Provider


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


class ProviderImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=ProviderFromCSVForm)


class ProviderBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Provider.objects.all(), widget=forms.MultipleHiddenInput)
    asn = forms.IntegerField(required=False, label='ASN')
    account = forms.CharField(max_length=30, required=False, label='Account number')
    portal_url = forms.URLField(required=False, label='Portal')
    noc_contact = forms.CharField(required=False, widget=SmallTextarea, label='NOC contact')
    admin_contact = forms.CharField(required=False, widget=SmallTextarea, label='Admin contact')
    comments = CommentField()


def provider_site_choices():
    site_choices = Site.objects.all()
    return [(s.slug, s.name) for s in site_choices]


class ProviderFilterForm(forms.Form, BootstrapMixin):
    site = forms.MultipleChoiceField(required=False, choices=provider_site_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))


#
# Circuit types
#

class CircuitTypeForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField()

    class Meta:
        model = CircuitType
        fields = ['name', 'slug']


#
# Circuits
#

class CircuitForm(BootstrapMixin, CustomFieldForm):
    site = forms.ModelChoiceField(queryset=Site.objects.all(), widget=forms.Select(attrs={'filter-for': 'rack'}))
    rack = forms.ModelChoiceField(queryset=Rack.objects.all(), required=False, label='Rack',
                                  widget=APISelect(api_url='/api/dcim/racks/?site_id={{site}}',
                                                   attrs={'filter-for': 'device'}))
    device = forms.ModelChoiceField(queryset=Device.objects.all(), required=False, label='Device',
                                    widget=APISelect(api_url='/api/dcim/devices/?rack_id={{rack}}',
                                                     attrs={'filter-for': 'interface'}))
    livesearch = forms.CharField(required=False, label='Device', widget=Livesearch(
        query_key='q', query_url='dcim-api:device_list', field_to_update='device')
    )
    interface = forms.ModelChoiceField(queryset=Interface.objects.all(), required=False, label='Interface',
                                       widget=APISelect(api_url='/api/dcim/devices/{{device}}/interfaces/?type=physical',
                                                        disabled_indicator='is_connected'))
    comments = CommentField()

    class Meta:
        model = Circuit
        fields = [
            'cid', 'type', 'provider', 'tenant', 'site', 'rack', 'device', 'livesearch', 'interface', 'install_date',
            'port_speed', 'upstream_speed', 'commit_rate', 'xconnect_id', 'pp_info', 'comments'
        ]
        help_texts = {
            'cid': "Unique circuit ID",
            'install_date': "Format: YYYY-MM-DD",
            'port_speed': "Physical circuit speed",
            'commit_rate': "Commited rate",
            'xconnect_id': "ID of the local cross-connect",
            'pp_info': "Patch panel ID and port number(s)"
        }

    def __init__(self, *args, **kwargs):

        super(CircuitForm, self).__init__(*args, **kwargs)

        # If this circuit has been assigned to an interface, initialize rack and device
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
                .exclude(form_factor=IFACE_FF_VIRTUAL).select_related('circuit', 'connected_as_a', 'connected_as_b')
            self.fields['interface'].widget.attrs['initial'] = self.data.get('interface')
        elif self.initial.get('device'):
            interfaces = Interface.objects.filter(device=self.initial['device'])\
                .exclude(form_factor=IFACE_FF_VIRTUAL).select_related('circuit', 'connected_as_a', 'connected_as_b')
            self.fields['interface'].widget.attrs['initial'] = self.initial.get('interface')
        else:
            interfaces = []
        self.fields['interface'].choices = [
            (iface.id, {
                'label': iface.name,
                'disabled': iface.is_connected and iface.id != self.fields['interface'].widget.attrs.get('initial'),
            }) for iface in interfaces
        ]


class CircuitFromCSVForm(forms.ModelForm):
    provider = forms.ModelChoiceField(Provider.objects.all(), to_field_name='name',
                                      error_messages={'invalid_choice': 'Provider not found.'})
    type = forms.ModelChoiceField(CircuitType.objects.all(), to_field_name='name',
                                  error_messages={'invalid_choice': 'Invalid circuit type.'})
    tenant = forms.ModelChoiceField(Tenant.objects.all(), to_field_name='name', required=False,
                                    error_messages={'invalid_choice': 'Tenant not found.'})
    site = forms.ModelChoiceField(Site.objects.all(), to_field_name='name',
                                  error_messages={'invalid_choice': 'Site not found.'})

    class Meta:
        model = Circuit
        fields = ['cid', 'provider', 'type', 'tenant', 'site', 'install_date', 'port_speed', 'upstream_speed',
                  'commit_rate', 'xconnect_id', 'pp_info']


class CircuitImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=CircuitFromCSVForm)


class CircuitBulkEditForm(BootstrapMixin, CustomFieldBulkEditForm):
    pk = forms.ModelMultipleChoiceField(queryset=Circuit.objects.all(), widget=forms.MultipleHiddenInput)
    type = forms.ModelChoiceField(queryset=CircuitType.objects.all(), required=False)
    provider = forms.ModelChoiceField(queryset=Provider.objects.all(), required=False)
    tenant = forms.TypedChoiceField(choices=bulkedit_tenant_choices, coerce=int, required=False, label='Tenant')
    port_speed = forms.IntegerField(required=False, label='Port speed (Kbps)')
    commit_rate = forms.IntegerField(required=False, label='Commit rate (Kbps)')
    comments = CommentField()


def circuit_type_choices():
    type_choices = CircuitType.objects.annotate(circuit_count=Count('circuits'))
    return [(t.slug, u'{} ({})'.format(t.name, t.circuit_count)) for t in type_choices]


def circuit_provider_choices():
    provider_choices = Provider.objects.annotate(circuit_count=Count('circuits'))
    return [(p.slug, u'{} ({})'.format(p.name, p.circuit_count)) for p in provider_choices]


def circuit_tenant_choices():
    tenant_choices = Tenant.objects.annotate(circuit_count=Count('circuits'))
    return [(t.slug, u'{} ({})'.format(t.name, t.circuit_count)) for t in tenant_choices]


def circuit_site_choices():
    site_choices = Site.objects.annotate(circuit_count=Count('circuits'))
    return [(s.slug, u'{} ({})'.format(s.name, s.circuit_count)) for s in site_choices]


class CircuitFilterForm(forms.Form, BootstrapMixin):
    type = forms.MultipleChoiceField(required=False, choices=circuit_type_choices)
    provider = forms.MultipleChoiceField(required=False, choices=circuit_provider_choices,
                                         widget=forms.SelectMultiple(attrs={'size': 8}))
    tenant = forms.MultipleChoiceField(required=False, choices=circuit_tenant_choices,
                                       widget=forms.SelectMultiple(attrs={'size': 8}))
    site = forms.MultipleChoiceField(required=False, choices=circuit_site_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))
