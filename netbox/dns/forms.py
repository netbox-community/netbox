from django import forms
from django.db.models import Count

from ipam.models import IPAddress
from utilities.forms import (
    BootstrapMixin, ConfirmationForm, APISelect, Livesearch, CSVDataField, BulkImportForm, SmallTextarea
)

from .models import (
    Zone,
    Record,
)

from .formfields import AddressFormField

#
# Zones
#


class ZoneForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = Zone
        fields = ['name', 'ttl', 'soa_name', 'soa_contact', 'soa_refresh', 'soa_retry', 'soa_expire', 'soa_minimum', 'extra_conf', 'description']
        labels = {
            'soa_name': 'SOA Name',
            'soa_contact': 'SOA Contact',
            'soa_refresh': 'SOA Refresh',
            'soa_retry': 'SOA Retry',
            'soa_expire': 'SOA Expire',
            'soa_minimum': 'SOA Minimum',
            'extra_conf': 'Extra Conf',
            'description': 'Description',
        }
        help_texts = {
            'ttl': "Time to live, in seconds",
            'soa_name': "The primary name server for the domain, @ for origin",
            'soa_contact': "The responsible party for the domain (e.g. ns.foo.net. noc.foo.net.)",
            'soa_refresh': "Refresh time, in seconds",
            'soa_retry': "Retry time, in seconds",
            'soa_expire': "Expire time, in seconds",
            'soa_minimum': "Negative result TTL, in seconds",
            'extra_conf': "Extra conf related to the zone, to put in your DNS server main conf file",
        }
        widgets = {
            'extra_conf': SmallTextarea(attrs={'rows': 3}),
        }


class ZoneFromCSVForm(forms.ModelForm):

    class Meta:
        model = Zone
        fields = ['name', 'ttl', 'soa_name', 'soa_contact', 'soa_refresh', 'soa_retry', 'soa_expire', 'soa_minimum', 'extra_conf', 'description']


class ZoneImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=ZoneFromCSVForm)


class ZoneBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=Zone.objects.all(), widget=forms.MultipleHiddenInput)
    name = forms.CharField(max_length=100, required=False, label='Name')
    ttl = forms.IntegerField(required=False, label='TTL')
    soa_name = forms.CharField(max_length=100, required=False, label='SOA Name')
    soa_contact = forms.CharField(max_length=100, required=False, label='SOA Contact')
    soa_refresh = forms.IntegerField(required=False, label='SOA Refresh')
    soa_retry = forms.IntegerField(required=False, label='SOA Retry')
    soa_expire = forms.IntegerField(required=False, label='SOA Expire')
    soa_minimum = forms.IntegerField(required=False, label='SOA Minimum')
    extra_conf = forms.CharField(max_length=500, required=False, widget=SmallTextarea(attrs={'rows': 3}), label='Extra Conf')
    description = forms.CharField(max_length=100, required=False, label='Description')


class ZoneBulkDeleteForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=Zone.objects.all(), widget=forms.MultipleHiddenInput)


class ZoneFilterForm(forms.Form, BootstrapMixin):
    pass

#
# Records
#


class RecordForm(forms.ModelForm, BootstrapMixin):

    address = AddressFormField(required=False)

    class Meta:
        model = Record
        fields = ['name', 'record_type', 'priority', 'zone', 'address', 'value', 'description']
        labels = {
            'record_type': 'Type',
        }
        help_texts = {
            'name': 'Host name, @ for origin (e.g. www)',
            'record_type': 'Record type (e.g. MX or AAAA)',
            'priority': 'Priority level (e.g. 10)',
            'zone': 'Zone the record belongs to',
            'address': 'IP address if value is an IP address, in AAAA records for instance',
            'value': 'Text value else, in CNAME records for instance'
        }


class RecordFromCSVForm(forms.ModelForm):

    zone = forms.ModelChoiceField(queryset=Zone.objects.all(), to_field_name='name', error_messages={'invalid_choice': 'Zone not found.'})
    address = AddressFormField(required=False)

    class Meta:
        model = Record
        fields = ['zone', 'name', 'record_type', 'priority', 'address', 'value', 'description']


class RecordImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=RecordFromCSVForm)


class RecordBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=Record.objects.all(), widget=forms.MultipleHiddenInput)
    name = forms.CharField(max_length=100, required=False, label='Name')
    record_type = forms.CharField(max_length=100, required=False, label='Type')
    priority = forms.IntegerField(required=False)
    zone = forms.ModelChoiceField(queryset=Zone.objects.all(), required=False)
    address = AddressFormField(required=False)
    value = forms.CharField(max_length=100, required=False)


class RecordBulkDeleteForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=Record.objects.all(), widget=forms.MultipleHiddenInput)


def record_zone_choices():
    zone_choices = Zone.objects.annotate(record_count=Count('records'))
    return [(z.name, '{} ({})'.format(z.name, z.record_count)) for z in zone_choices]


def record_type_choices():
    type_choices = {}
    records = Record.objects.all()
    for r in records:
        if r.record_type not in type_choices:
            type_choices[r.record_type] = 1
        else:
            type_choices[r.record_type] += 1
    return [(t, '{} ({})'.format(t, count)) for t, count in type_choices.items()]


class RecordFilterForm(forms.Form, BootstrapMixin):
    zone__name = forms.MultipleChoiceField(required=False, choices=record_zone_choices, label='Zone',
                                           widget=forms.SelectMultiple(attrs={'size': 8}))
    record_type = forms.MultipleChoiceField(required=False, choices=record_type_choices, label='Type',
                                            widget=forms.SelectMultiple(attrs={'size': 8}))
