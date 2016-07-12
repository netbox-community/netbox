from netaddr import IPNetwork

from django import forms
from django.db.models import Count

from dcim.models import Site, Device, Interface
from utilities.forms import (
    BootstrapMixin, ConfirmationForm, APISelect, Livesearch, CSVDataField, BulkImportForm, SlugField,
)

from .models import (
    Aggregate, IPAddress, Prefix, PREFIX_STATUS_CHOICES, RIR, Role, VLAN, VLAN_STATUS_CHOICES, VRF,
)


FORM_PREFIX_STATUS_CHOICES = (('', '---------'),) + PREFIX_STATUS_CHOICES
FORM_VLAN_STATUS_CHOICES = (('', '---------'),) + VLAN_STATUS_CHOICES


#
# VRFs
#

class VRFForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = VRF
        fields = ['name', 'rd', 'description']
        labels = {
            'rd': "RD",
        }
        help_texts = {
            'rd': "Route distinguisher in any format",
        }


class VRFFromCSVForm(forms.ModelForm):

    class Meta:
        model = VRF
        fields = ['name', 'rd', 'description']


class VRFImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=VRFFromCSVForm)


class VRFBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=VRF.objects.all(), widget=forms.MultipleHiddenInput)
    description = forms.CharField(max_length=100, required=False)


class VRFBulkDeleteForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=VRF.objects.all(), widget=forms.MultipleHiddenInput)


#
# RIRs
#

class RIRForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField()

    class Meta:
        model = RIR
        fields = ['name', 'slug']


class RIRBulkDeleteForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=RIR.objects.all(), widget=forms.MultipleHiddenInput)


#
# Aggregates
#

class AggregateForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = Aggregate
        fields = ['prefix', 'rir', 'date_added', 'description']
        help_texts = {
            'prefix': "IPv4 or IPv6 network",
            'rir': "Regional Internet Registry responsible for this prefix",
            'date_added': "Format: YYYY-MM-DD",
        }


class AggregateFromCSVForm(forms.ModelForm):
    rir = forms.ModelChoiceField(queryset=RIR.objects.all(), to_field_name='name',
                                 error_messages={'invalid_choice': 'RIR not found.'})

    class Meta:
        model = Aggregate
        fields = ['prefix', 'rir', 'date_added', 'description']


class AggregateImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=AggregateFromCSVForm)


class AggregateBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=Aggregate.objects.all(), widget=forms.MultipleHiddenInput)
    rir = forms.ModelChoiceField(queryset=RIR.objects.all(), required=False, label='RIR')
    date_added = forms.DateField(required=False)
    description = forms.CharField(max_length=50, required=False)


class AggregateBulkDeleteForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=Aggregate.objects.all(), widget=forms.MultipleHiddenInput)


def aggregate_rir_choices():
    rir_choices = RIR.objects.annotate(aggregate_count=Count('aggregates'))
    return [(r.slug, '{} ({})'.format(r.name, r.aggregate_count)) for r in rir_choices]


class AggregateFilterForm(forms.Form, BootstrapMixin):
    rir = forms.MultipleChoiceField(required=False, choices=aggregate_rir_choices, label='RIR',
                                    widget=forms.SelectMultiple(attrs={'size': 8}))


#
# Roles
#

class RoleForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField()

    class Meta:
        model = Role
        fields = ['name', 'slug']


class RoleBulkDeleteForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=Role.objects.all(), widget=forms.MultipleHiddenInput)


#
# Prefixes
#

class PrefixForm(forms.ModelForm, BootstrapMixin):
    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=False, label='Site',
                                  widget=forms.Select(attrs={'filter-for': 'vlan'}))
    vlan = forms.ModelChoiceField(queryset=VLAN.objects.all(), required=False, label='VLAN',
                                  widget=APISelect(api_url='/api/ipam/vlans/?site_id={{site}}',
                                                   display_field='display_name'))

    class Meta:
        model = Prefix
        fields = ['prefix', 'vrf', 'site', 'vlan', 'status', 'role', 'description']
        help_texts = {
            'prefix': "IPv4 or IPv6 network",
            'vrf': "VRF (if applicable)",
            'site': "The site to which this prefix is assigned (if applicable)",
            'vlan': "The VLAN to which this prefix is assigned (if applicable)",
            'status': "Operational status of this prefix",
            'role': "The primary function of this prefix",
        }

    def __init__(self, *args, **kwargs):
        super(PrefixForm, self).__init__(*args, **kwargs)

        self.fields['vrf'].empty_label = 'Global'

        # Initialize field without choices to avoid pulling all VLANs from the database
        if self.is_bound and self.data.get('site'):
            self.fields['vlan'].queryset = VLAN.objects.filter(site__pk=self.data['site'])
        elif self.initial.get('site'):
            self.fields['vlan'].queryset = VLAN.objects.filter(site=self.initial['site'])
        else:
            self.fields['vlan'].choices = []

    def clean_prefix(self):
        data = self.cleaned_data['prefix']
        try:
            prefix = IPNetwork(data)
        except:
            raise
        if prefix.version == 4 and prefix.prefixlen == 32:
            raise forms.ValidationError("Cannot create host addresses (/32) as prefixes. These should be IPv4 "
                                        "addresses instead.")
        elif prefix.version == 6 and prefix.prefixlen == 128:
            raise forms.ValidationError("Cannot create host addresses (/128) as prefixes. These should be IPv6 "
                                        "addresses instead.")
        return data


class PrefixFromCSVForm(forms.ModelForm):
    vrf = forms.ModelChoiceField(queryset=VRF.objects.all(), required=False, to_field_name='rd',
                                 error_messages={'invalid_choice': 'VRF not found.'})
    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=False, to_field_name='name',
                                  error_messages={'invalid_choice': 'Site not found.'})
    status_name = forms.ChoiceField(choices=[(s[1], s[0]) for s in PREFIX_STATUS_CHOICES])
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False, to_field_name='name',
                                  error_messages={'invalid_choice': 'Invalid role.'})

    class Meta:
        model = Prefix
        fields = ['prefix', 'vrf', 'site', 'status_name', 'role', 'description']

    def save(self, *args, **kwargs):
        m = super(PrefixFromCSVForm, self).save(commit=False)
        # Assign Prefix status by name
        m.status = dict(self.fields['status_name'].choices)[self.cleaned_data['status_name']]
        if kwargs.get('commit'):
            m.save()
        return m


class PrefixImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=PrefixFromCSVForm)


class PrefixBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=Prefix.objects.all(), widget=forms.MultipleHiddenInput)
    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=False)
    vrf = forms.ModelChoiceField(queryset=VRF.objects.all(), required=False, label='VRF',
                                 help_text="Select the VRF to assign, or check below to remove VRF assignment")
    vrf_global = forms.BooleanField(required=False, label='Set VRF to global')
    status = forms.ChoiceField(choices=FORM_PREFIX_STATUS_CHOICES, required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False)
    description = forms.CharField(max_length=50, required=False)


class PrefixBulkDeleteForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=Prefix.objects.all(), widget=forms.MultipleHiddenInput)


def prefix_vrf_choices():
    vrf_choices = [('', 'All'), (0, 'Global')]
    vrf_choices += [(v.pk, v.name) for v in VRF.objects.all()]
    return vrf_choices


def prefix_site_choices():
    site_choices = Site.objects.annotate(prefix_count=Count('prefixes'))
    return [(s.slug, '{} ({})'.format(s.name, s.prefix_count)) for s in site_choices]


def prefix_status_choices():
    status_counts = {}
    for status in Prefix.objects.values('status').annotate(count=Count('status')).order_by('status'):
        status_counts[status['status']] = status['count']
    return [(s[0], '{} ({})'.format(s[1], status_counts.get(s[0], 0))) for s in PREFIX_STATUS_CHOICES]


def prefix_role_choices():
    role_choices = Role.objects.annotate(prefix_count=Count('prefixes'))
    return [(r.slug, '{} ({})'.format(r.name, r.prefix_count)) for r in role_choices]


class PrefixFilterForm(forms.Form, BootstrapMixin):
    parent = forms.CharField(required=False, label='Search Within')
    vrf = forms.ChoiceField(required=False, choices=prefix_vrf_choices, label='VRF')
    status = forms.MultipleChoiceField(required=False, choices=prefix_status_choices)
    site = forms.MultipleChoiceField(required=False, choices=prefix_site_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))
    role = forms.MultipleChoiceField(required=False, choices=prefix_role_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))
    expand = forms.BooleanField(required=False, label='Expand prefix hierarchy')


#
# IP addresses
#

class IPAddressForm(forms.ModelForm, BootstrapMixin):
    nat_site = forms.ModelChoiceField(queryset=Site.objects.all(), required=False, label='Site',
                                      widget=forms.Select(attrs={'filter-for': 'nat_device'}))
    nat_device = forms.ModelChoiceField(queryset=Device.objects.all(), required=False, label='Device',
                                        widget=APISelect(api_url='/api/dcim/devices/?site_id={{nat_site}}',
                                                         attrs={'filter-for': 'nat_inside'}))
    livesearch = forms.CharField(required=False, label='IP Address', widget=Livesearch(
        query_key='q', query_url='ipam-api:ipaddress_list', field_to_update='nat_inside', obj_label='address')
    )
    nat_inside = forms.ModelChoiceField(queryset=IPAddress.objects.all(), required=False, label='NAT (Inside)',
                                        widget=APISelect(api_url='/api/ipam/ip-addresses/?device_id={{nat_device}}',
                                                         display_field='address'))

    class Meta:
        model = IPAddress
        fields = ['address', 'vrf', 'nat_device', 'nat_inside', 'description']
        help_texts = {
            'address': "IPv4 or IPv6 address and mask",
            'vrf': "VRF (if applicable)",
        }

    def __init__(self, *args, **kwargs):
        super(IPAddressForm, self).__init__(*args, **kwargs)

        self.fields['vrf'].empty_label = 'Global'

        if self.instance.nat_inside:

            nat_inside = self.instance.nat_inside
            # If the IP is assigned to an interface, populate site/device fields accordingly
            if self.instance.nat_inside.interface:
                self.initial['nat_site'] = self.instance.nat_inside.interface.device.rack.site.pk
                self.initial['nat_device'] = self.instance.nat_inside.interface.device.pk
                self.fields['nat_device'].queryset = Device.objects.filter(
                    rack__site=nat_inside.interface.device.rack.site)
                self.fields['nat_inside'].queryset = IPAddress.objects.filter(
                    interface__device=nat_inside.interface.device)
            else:
                self.fields['nat_inside'].queryset = IPAddress.objects.filter(pk=nat_inside.pk)

        else:

            # Initialize nat_device choices if nat_site is set
            if self.is_bound and self.data.get('nat_site'):
                self.fields['nat_device'].queryset = Device.objects.filter(rack__site__pk=self.data['nat_site'])
            elif self.initial.get('nat_site'):
                self.fields['nat_device'].queryset = Device.objects.filter(rack__site=self.initial['nat_site'])
            else:
                self.fields['nat_device'].choices = []

            # Initialize nat_inside choices if nat_device is set
            if self.is_bound and self.data.get('nat_device'):
                self.fields['nat_inside'].queryset = IPAddress.objects.filter(
                    interface__device__pk=self.data['nat_device'])
            elif self.initial.get('nat_device'):
                self.fields['nat_inside'].queryset = IPAddress.objects.filter(
                    interface__device__pk=self.initial['nat_device'])
            else:
                self.fields['nat_inside'].choices = []


class IPAddressFromCSVForm(forms.ModelForm):
    vrf = forms.ModelChoiceField(queryset=VRF.objects.all(), required=False, to_field_name='rd',
                                 error_messages={'invalid_choice': 'VRF not found.'})
    device = forms.ModelChoiceField(queryset=Device.objects.all(), required=False, to_field_name='name',
                                    error_messages={'invalid_choice': 'Device not found.'})
    interface_name = forms.CharField(required=False)
    is_primary = forms.BooleanField(required=False)

    class Meta:
        model = IPAddress
        fields = ['address', 'vrf', 'device', 'interface_name', 'is_primary', 'description']

    def clean(self):

        device = self.cleaned_data.get('device')
        interface_name = self.cleaned_data.get('interface_name')
        is_primary = self.cleaned_data.get('is_primary')

        # Validate interface
        if device and interface_name:
            try:
                Interface.objects.get(device=device, name=interface_name)
            except Interface.DoesNotExist:
                self.add_error('interface_name', "Invalid interface ({}) for {}".format(interface_name, device))
        elif device and not interface_name:
            self.add_error('interface_name', "Device set ({}) but interface missing".format(device))
        elif interface_name and not device:
            self.add_error('device', "Interface set ({}) but device missing or invalid".format(interface_name))

        # Validate is_primary
        if is_primary and not device:
            self.add_error('is_primary', "No device specified; cannot set as primary IP")

    def save(self, commit=True):

        # Set interface
        if self.cleaned_data['device'] and self.cleaned_data['interface_name']:
            self.instance.interface = Interface.objects.get(device=self.cleaned_data['device'],
                                                            name=self.cleaned_data['interface_name'])
        # Set as primary for device
        if self.cleaned_data['is_primary']:
            if self.instance.family == 4:
                self.instance.primary_ip4_for = self.cleaned_data['device']
            elif self.instance.family == 6:
                self.instance.primary_ip6_for = self.cleaned_data['device']

        return super(IPAddressFromCSVForm, self).save(commit=commit)


class IPAddressImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=IPAddressFromCSVForm)


class IPAddressBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=IPAddress.objects.all(), widget=forms.MultipleHiddenInput)
    vrf = forms.ModelChoiceField(queryset=VRF.objects.all(), required=False, label='VRF',
                                 help_text="Select the VRF to assign, or check below to remove VRF assignment")
    vrf_global = forms.BooleanField(required=False, label='Set VRF to global')
    description = forms.CharField(max_length=50, required=False)


class IPAddressBulkDeleteForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=IPAddress.objects.all(), widget=forms.MultipleHiddenInput)


def ipaddress_family_choices():
    return [('', 'All'), (4, 'IPv4'), (6, 'IPv6')]


def ipaddress_vrf_choices():
    vrf_choices = [('', 'All'), (0, 'Global')]
    vrf_choices += [(v.pk, v.name) for v in VRF.objects.all()]
    return vrf_choices


class IPAddressFilterForm(forms.Form, BootstrapMixin):
    family = forms.ChoiceField(required=False, choices=ipaddress_family_choices, label='Address Family')
    vrf = forms.ChoiceField(required=False, choices=ipaddress_vrf_choices, label='VRF')


#
# VLANs
#

class VLANForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = VLAN
        fields = ['site', 'vid', 'name', 'status', 'role']
        help_texts = {
            'site': "The site at which this VLAN exists",
            'vid': "Configured VLAN ID",
            'name': "Configured VLAN name",
            'status': "Operational status of this VLAN",
            'role': "The primary function of this VLAN",
        }


class VLANFromCSVForm(forms.ModelForm):
    site = forms.ModelChoiceField(queryset=Site.objects.all(), to_field_name='name',
                                  error_messages={'invalid_choice': 'Device not found.'})
    status_name = forms.ChoiceField(choices=[(s[1], s[0]) for s in VLAN_STATUS_CHOICES])
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False, to_field_name='name',
                                  error_messages={'invalid_choice': 'Invalid role.'})

    class Meta:
        model = VLAN
        fields = ['site', 'vid', 'name', 'status_name', 'role']

    def save(self, *args, **kwargs):
        m = super(VLANFromCSVForm, self).save(commit=False)
        # Assign VLAN status by name
        m.status = dict(self.fields['status_name'].choices)[self.cleaned_data['status_name']]
        if kwargs.get('commit'):
            m.save()
        return m


class VLANImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=VLANFromCSVForm)


class VLANBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=VLAN.objects.all(), widget=forms.MultipleHiddenInput)
    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=False)
    status = forms.ChoiceField(choices=FORM_VLAN_STATUS_CHOICES, required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False)


class VLANBulkDeleteForm(ConfirmationForm):
    pk = forms.ModelMultipleChoiceField(queryset=VLAN.objects.all(), widget=forms.MultipleHiddenInput)


def vlan_site_choices():
    site_choices = Site.objects.annotate(vlan_count=Count('vlans'))
    return [(s.slug, '{} ({})'.format(s.name, s.vlan_count)) for s in site_choices]


def vlan_status_choices():
    status_counts = {}
    for status in VLAN.objects.values('status').annotate(count=Count('status')).order_by('status'):
        status_counts[status['status']] = status['count']
    return [(s[0], '{} ({})'.format(s[1], status_counts.get(s[0], 0))) for s in VLAN_STATUS_CHOICES]


def vlan_role_choices():
    role_choices = Role.objects.annotate(vlan_count=Count('vlans'))
    return [(r.slug, '{} ({})'.format(r.name, r.vlan_count)) for r in role_choices]


class VLANFilterForm(forms.Form, BootstrapMixin):
    site = forms.MultipleChoiceField(required=False, choices=vlan_site_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))
    status = forms.MultipleChoiceField(required=False, choices=vlan_status_choices)
    role = forms.MultipleChoiceField(required=False, choices=vlan_role_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))
