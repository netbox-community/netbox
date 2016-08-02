from netaddr import IPNetwork

from django import forms
from django.db.models import Count

from dcim.models import Site, Device, Interface
from tenancy.forms import bulkedit_tenant_choices
from tenancy.models import Tenant
from utilities.forms import BootstrapMixin, APISelect, Livesearch, CSVDataField, BulkImportForm, SlugField

from .models import (
    Aggregate, IPAddress, Prefix, PREFIX_STATUS_CHOICES, RIR, Role, VLAN, VLANGroup, VLAN_STATUS_CHOICES, VRF,
)


FORM_PREFIX_STATUS_CHOICES = (('', '---------'),) + PREFIX_STATUS_CHOICES
FORM_VLAN_STATUS_CHOICES = (('', '---------'),) + VLAN_STATUS_CHOICES


def bulkedit_vrf_choices():
    """
    Include an option to assign the object to the global table.
    """
    choices = [
        (None, '---------'),
        (0, 'Global'),
    ]
    choices += [(v.pk, v.name) for v in VRF.objects.all()]
    return choices


#
# VRFs
#

class VRFForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = VRF
        fields = ['name', 'rd', 'tenant', 'enforce_unique', 'description']
        labels = {
            'rd': "RD",
        }
        help_texts = {
            'rd': "Route distinguisher in any format",
        }


class VRFFromCSVForm(forms.ModelForm):
    tenant = forms.ModelChoiceField(Tenant.objects.all(), to_field_name='name', required=False,
                                    error_messages={'invalid_choice': 'Tenant not found.'})

    class Meta:
        model = VRF
        fields = ['name', 'rd', 'tenant', 'enforce_unique', 'description']


class VRFImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=VRFFromCSVForm)


class VRFBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=VRF.objects.all(), widget=forms.MultipleHiddenInput)
    tenant = forms.TypedChoiceField(choices=bulkedit_tenant_choices, coerce=int, required=False, label='Tenant')
    description = forms.CharField(max_length=100, required=False)


def vrf_tenant_choices():
    tenant_choices = Tenant.objects.annotate(vrf_count=Count('vrfs'))
    return [(t.slug, u'{} ({})'.format(t.name, t.vrf_count)) for t in tenant_choices]


class VRFFilterForm(forms.Form, BootstrapMixin):
    tenant = forms.MultipleChoiceField(required=False, choices=vrf_tenant_choices,
                                       widget=forms.SelectMultiple(attrs={'size': 8}))


#
# RIRs
#

class RIRForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField()

    class Meta:
        model = RIR
        fields = ['name', 'slug']


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
    description = forms.CharField(max_length=100, required=False)


def aggregate_rir_choices():
    rir_choices = RIR.objects.annotate(aggregate_count=Count('aggregates'))
    return [(r.slug, u'{} ({})'.format(r.name, r.aggregate_count)) for r in rir_choices]


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
        fields = ['prefix', 'vrf', 'tenant', 'site', 'vlan', 'status', 'role', 'description']
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
    tenant = forms.ModelChoiceField(Tenant.objects.all(), to_field_name='name', required=False,
                                    error_messages={'invalid_choice': 'Tenant not found.'})
    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=False, to_field_name='name',
                                  error_messages={'invalid_choice': 'Site not found.'})
    vlan_group_name = forms.CharField(required=False)
    vlan_vid = forms.IntegerField(required=False)
    status_name = forms.ChoiceField(choices=[(s[1], s[0]) for s in PREFIX_STATUS_CHOICES])
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False, to_field_name='name',
                                  error_messages={'invalid_choice': 'Invalid role.'})

    class Meta:
        model = Prefix
        fields = ['prefix', 'vrf', 'tenant', 'site', 'vlan_group_name', 'vlan_vid', 'status_name', 'role',
                  'description']

    def clean(self):

        super(PrefixFromCSVForm, self).clean()

        site = self.cleaned_data.get('site')
        vlan_group_name = self.cleaned_data.get('vlan_group_name')
        vlan_vid = self.cleaned_data.get('vlan_vid')

        # Validate VLAN
        vlan_group = None
        if vlan_group_name:
            try:
                vlan_group = VLANGroup.objects.get(site=site, name=vlan_group_name)
            except VLANGroup.DoesNotExist:
                self.add_error('vlan_group_name', "Invalid VLAN group ({} - {}).".format(site, vlan_group_name))
        if vlan_vid and vlan_group:
            try:
                self.instance.vlan = VLAN.objects.get(group=vlan_group, vid=vlan_vid)
            except VLAN.DoesNotExist:
                self.add_error('vlan_vid', "Invalid VLAN ID ({} - {}).".format(vlan_group, vlan_vid))
        elif vlan_vid and site:
            try:
                self.instance.vlan = VLAN.objects.get(site=site, vid=vlan_vid)
            except VLAN.MultipleObjectsReturned:
                self.add_error('vlan_vid', "Multiple VLANs found ({} - VID {})".format(site, vlan_vid))
        elif vlan_vid:
            self.add_error('vlan_vid', "Must specify site and/or VLAN group when assigning a VLAN.")

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
    vrf = forms.TypedChoiceField(choices=bulkedit_vrf_choices, coerce=int, required=False, label='VRF')
    tenant = forms.TypedChoiceField(choices=bulkedit_tenant_choices, coerce=int, required=False, label='Tenant')
    status = forms.ChoiceField(choices=FORM_PREFIX_STATUS_CHOICES, required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False)
    description = forms.CharField(max_length=100, required=False)


def prefix_vrf_choices():
    vrf_choices = VRF.objects.annotate(prefix_count=Count('prefixes'))
    return [(v.pk, u'{} ({})'.format(v.name, v.prefix_count)) for v in vrf_choices]


def tenant_choices():
    tenant_choices = Tenant.objects.all()
    return [(t.slug, t.name) for t in tenant_choices]


def prefix_site_choices():
    site_choices = Site.objects.annotate(prefix_count=Count('prefixes'))
    return [(s.slug, u'{} ({})'.format(s.name, s.prefix_count)) for s in site_choices]


def prefix_status_choices():
    status_counts = {}
    for status in Prefix.objects.values('status').annotate(count=Count('status')).order_by('status'):
        status_counts[status['status']] = status['count']
    return [(s[0], u'{} ({})'.format(s[1], status_counts.get(s[0], 0))) for s in PREFIX_STATUS_CHOICES]


def prefix_role_choices():
    role_choices = Role.objects.annotate(prefix_count=Count('prefixes'))
    return [(r.slug, u'{} ({})'.format(r.name, r.prefix_count)) for r in role_choices]


class PrefixFilterForm(forms.Form, BootstrapMixin):
    parent = forms.CharField(required=False, label='Search Within')
    vrf = forms.MultipleChoiceField(required=False, choices=prefix_vrf_choices, label='VRF',
                                    widget=forms.SelectMultiple(attrs={'size': 6}))
    tenant = forms.MultipleChoiceField(required=False, choices=tenant_choices, label='Tenant',
                                       widget=forms.SelectMultiple(attrs={'size': 6}))
    status = forms.MultipleChoiceField(required=False, choices=prefix_status_choices,
                                       widget=forms.SelectMultiple(attrs={'size': 6}))
    site = forms.MultipleChoiceField(required=False, choices=prefix_site_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 6}))
    role = forms.MultipleChoiceField(required=False, choices=prefix_role_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 6}))
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
        fields = ['address', 'vrf', 'tenant', 'nat_device', 'nat_inside', 'description']
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
    tenant = forms.ModelChoiceField(Tenant.objects.all(), to_field_name='name', required=False,
                                    error_messages={'invalid_choice': 'Tenant not found.'})
    device = forms.ModelChoiceField(queryset=Device.objects.all(), required=False, to_field_name='name',
                                    error_messages={'invalid_choice': 'Device not found.'})
    interface_name = forms.CharField(required=False)
    is_primary = forms.BooleanField(required=False)

    class Meta:
        model = IPAddress
        fields = ['address', 'vrf', 'tenant', 'device', 'interface_name', 'is_primary', 'description']

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
            if self.instance.address.version == 4:
                self.instance.primary_ip4_for = self.cleaned_data['device']
            elif self.instance.address.version == 6:
                self.instance.primary_ip6_for = self.cleaned_data['device']

        return super(IPAddressFromCSVForm, self).save(commit=commit)


class IPAddressImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=IPAddressFromCSVForm)


class IPAddressBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=IPAddress.objects.all(), widget=forms.MultipleHiddenInput)
    vrf = forms.TypedChoiceField(choices=bulkedit_vrf_choices, coerce=int, required=False, label='VRF')
    tenant = forms.TypedChoiceField(choices=bulkedit_tenant_choices, coerce=int, required=False, label='Tenant')
    description = forms.CharField(max_length=100, required=False)


def ipaddress_family_choices():
    return [('', 'All'), (4, 'IPv4'), (6, 'IPv6')]


def ipaddress_vrf_choices():
    vrf_choices = VRF.objects.annotate(ipaddress_count=Count('ip_addresses'))
    return [(v.pk, u'{} ({})'.format(v.name, v.ipaddress_count)) for v in vrf_choices]


class IPAddressFilterForm(forms.Form, BootstrapMixin):
    family = forms.ChoiceField(required=False, choices=ipaddress_family_choices, label='Address Family')
    vrf = forms.MultipleChoiceField(required=False, choices=ipaddress_vrf_choices, label='VRF',
                                    widget=forms.SelectMultiple(attrs={'size': 6}))
    tenant = forms.MultipleChoiceField(required=False, choices=tenant_choices, label='Tenant',
                                       widget=forms.SelectMultiple(attrs={'size': 6}))


#
# VLAN groups
#

class VLANGroupForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField()

    class Meta:
        model = VLANGroup
        fields = ['site', 'name', 'slug']


def vlangroup_site_choices():
    site_choices = Site.objects.annotate(vlangroup_count=Count('vlan_groups'))
    return [(s.slug, u'{} ({})'.format(s.name, s.vlangroup_count)) for s in site_choices]


class VLANGroupFilterForm(forms.Form, BootstrapMixin):
    site = forms.MultipleChoiceField(required=False, choices=vlangroup_site_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))


#
# VLANs
#

class VLANForm(forms.ModelForm, BootstrapMixin):
    group = forms.ModelChoiceField(queryset=VLANGroup.objects.all(), required=False, label='Group', widget=APISelect(
        api_url='/api/ipam/vlan-groups/?site_id={{site}}',
    ))

    class Meta:
        model = VLAN
        fields = ['site', 'group', 'vid', 'name', 'tenant', 'status', 'role', 'description']
        help_texts = {
            'site': "The site at which this VLAN exists",
            'group': "VLAN group (optional)",
            'vid': "Configured VLAN ID",
            'name': "Configured VLAN name",
            'status': "Operational status of this VLAN",
            'role': "The primary function of this VLAN",
        }
        widgets = {
            'site': forms.Select(attrs={'filter-for': 'group'}),
        }

    def __init__(self, *args, **kwargs):

        super(VLANForm, self).__init__(*args, **kwargs)

        # Limit VLAN group choices
        if self.is_bound and self.data.get('site'):
            self.fields['group'].queryset = VLANGroup.objects.filter(site__pk=self.data['site'])
        elif self.initial.get('site'):
            self.fields['group'].queryset = VLANGroup.objects.filter(site=self.initial['site'])
        else:
            self.fields['group'].choices = []


class VLANFromCSVForm(forms.ModelForm):
    site = forms.ModelChoiceField(queryset=Site.objects.all(), to_field_name='name',
                                  error_messages={'invalid_choice': 'Device not found.'})
    group = forms.ModelChoiceField(queryset=VLANGroup.objects.all(), required=False, to_field_name='name',
                                   error_messages={'invalid_choice': 'VLAN group not found.'})
    tenant = forms.ModelChoiceField(Tenant.objects.all(), to_field_name='name', required=False,
                                    error_messages={'invalid_choice': 'Tenant not found.'})
    status_name = forms.ChoiceField(choices=[(s[1], s[0]) for s in VLAN_STATUS_CHOICES])
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False, to_field_name='name',
                                  error_messages={'invalid_choice': 'Invalid role.'})

    class Meta:
        model = VLAN
        fields = ['site', 'group', 'vid', 'name', 'tenant', 'status_name', 'role', 'description']

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
    group = forms.ModelChoiceField(queryset=VLANGroup.objects.all(), required=False)
    tenant = forms.TypedChoiceField(choices=bulkedit_tenant_choices, coerce=int, required=False, label='Tenant')
    status = forms.ChoiceField(choices=FORM_VLAN_STATUS_CHOICES, required=False)
    role = forms.ModelChoiceField(queryset=Role.objects.all(), required=False)
    description = forms.CharField(max_length=100, required=False)


def vlan_site_choices():
    site_choices = Site.objects.annotate(vlan_count=Count('vlans'))
    return [(s.slug, u'{} ({})'.format(s.name, s.vlan_count)) for s in site_choices]


def vlan_group_choices():
    group_choices = VLANGroup.objects.select_related('site').annotate(vlan_count=Count('vlans'))
    return [(g.pk, u'{} ({})'.format(g, g.vlan_count)) for g in group_choices]


def vlan_tenant_choices():
    tenant_choices = Tenant.objects.annotate(vrf_count=Count('vlans'))
    return [(t.slug, u'{} ({})'.format(t.name, t.vrf_count)) for t in tenant_choices]


def vlan_status_choices():
    status_counts = {}
    for status in VLAN.objects.values('status').annotate(count=Count('status')).order_by('status'):
        status_counts[status['status']] = status['count']
    return [(s[0], u'{} ({})'.format(s[1], status_counts.get(s[0], 0))) for s in VLAN_STATUS_CHOICES]


def vlan_role_choices():
    role_choices = Role.objects.annotate(vlan_count=Count('vlans'))
    return [(r.slug, u'{} ({})'.format(r.name, r.vlan_count)) for r in role_choices]


class VLANFilterForm(forms.Form, BootstrapMixin):
    site = forms.MultipleChoiceField(required=False, choices=vlan_site_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))
    group_id = forms.MultipleChoiceField(required=False, choices=vlan_group_choices, label='VLAN Group',
                                         widget=forms.SelectMultiple(attrs={'size': 8}))
    tenant = forms.MultipleChoiceField(required=False, choices=vlan_tenant_choices,
                                       widget=forms.SelectMultiple(attrs={'size': 8}))
    status = forms.MultipleChoiceField(required=False, choices=vlan_status_choices)
    role = forms.MultipleChoiceField(required=False, choices=vlan_role_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))
