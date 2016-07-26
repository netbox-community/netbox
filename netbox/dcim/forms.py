import re

from django import forms
from django.db.models import Count, Q

from ipam.models import IPAddress
from utilities.forms import (
    APISelect, BootstrapMixin, BulkImportForm, CommentField, CSVDataField, ExpandableNameField,
    FlexibleModelChoiceField, Livesearch, SelectWithDisabled, SmallTextarea, SlugField,
)

from .models import (
    DeviceBay, DeviceBayTemplate, CONNECTION_STATUS_CHOICES, CONNECTION_STATUS_PLANNED, CONNECTION_STATUS_CONNECTED,
    ConsolePort, ConsolePortTemplate, ConsoleServerPort, ConsoleServerPortTemplate, Device, DeviceRole, DeviceType,
    Interface, IFACE_FF_VIRTUAL, InterfaceConnection, InterfaceTemplate, Manufacturer, Module, Platform, PowerOutlet,
    PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack, RackGroup, Site, STATUS_CHOICES, SUBDEVICE_ROLE_CHILD
)


FORM_STATUS_CHOICES = [
    ['', '---------'],
]

FORM_STATUS_CHOICES += STATUS_CHOICES

DEVICE_BY_PK_RE = '{\d+\}'


def get_device_by_name_or_pk(name):
    """
    Attempt to retrieve a device by either its name or primary key ('{pk}').
    """
    if re.match(DEVICE_BY_PK_RE, name):
        pk = name.strip('{}')
        device = Device.objects.get(pk=pk)
    else:
        device = Device.objects.get(name=name)
    return device


#
# Sites
#

class SiteForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField()
    comments = CommentField()

    class Meta:
        model = Site
        fields = ['name', 'slug', 'facility', 'asn', 'physical_address', 'shipping_address', 'comments']
        widgets = {
            'physical_address': SmallTextarea(attrs={'rows': 3}),
            'shipping_address': SmallTextarea(attrs={'rows': 3}),
        }
        help_texts = {
            'name': "Full name of the site",
            'facility': "Data center provider and facility (e.g. Equinix NY7)",
            'asn': "BGP autonomous system number",
            'physical_address': "Physical location of the building (e.g. for GPS)",
            'shipping_address': "If different from the physical address"
        }


class SiteFromCSVForm(forms.ModelForm):

    class Meta:
        model = Site
        fields = ['name', 'slug', 'facility', 'asn']


class SiteImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=SiteFromCSVForm)


#
# Rack groups
#

class RackGroupForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField()

    class Meta:
        model = RackGroup
        fields = ['site', 'name', 'slug']


def rackgroup_site_choices():
    site_choices = Site.objects.annotate(rack_count=Count('rack_groups'))
    return [(s.slug, u'{} ({})'.format(s.name, s.rack_count)) for s in site_choices]


class RackGroupFilterForm(forms.Form, BootstrapMixin):
    site = forms.MultipleChoiceField(required=False, choices=rackgroup_site_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))


#
# Racks
#

class RackForm(forms.ModelForm, BootstrapMixin):
    group = forms.ModelChoiceField(queryset=RackGroup.objects.all(), required=False, label='Group', widget=APISelect(
        api_url='/api/dcim/rack-groups/?site_id={{site}}',
    ))
    comments = CommentField()

    class Meta:
        model = Rack
        fields = ['site', 'group', 'name', 'facility_id', 'u_height', 'comments']
        help_texts = {
            'site': "The site at which the rack exists",
            'name': "Organizational rack name",
            'facility_id': "The unique rack ID assigned by the facility",
            'u_height': "Height in rack units",
        }
        widgets = {
            'site': forms.Select(attrs={'filter-for': 'group'}),
        }

    def __init__(self, *args, **kwargs):

        super(RackForm, self).__init__(*args, **kwargs)

        # Limit rack group choices
        if self.is_bound and self.data.get('site'):
            self.fields['group'].queryset = RackGroup.objects.filter(site__pk=self.data['site'])
        elif self.initial.get('site'):
            self.fields['group'].queryset = RackGroup.objects.filter(site=self.initial['site'])
        else:
            self.fields['group'].choices = []


class RackFromCSVForm(forms.ModelForm):
    site = forms.ModelChoiceField(queryset=Site.objects.all(), to_field_name='name',
                                  error_messages={'invalid_choice': 'Site not found.'})
    group_name = forms.CharField(required=False)

    class Meta:
        model = Rack
        fields = ['site', 'group_name', 'name', 'facility_id', 'u_height']

    def clean(self):

        site = self.cleaned_data.get('site')
        group = self.cleaned_data.get('group_name')

        # Validate rack group
        if site and group:
            try:
                self.instance.group = RackGroup.objects.get(site=site, name=group)
            except RackGroup.DoesNotExist:
                self.add_error('group_name', "Invalid rack group ({})".format(group))


class RackImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=RackFromCSVForm)


class RackBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=Rack.objects.all(), widget=forms.MultipleHiddenInput)
    site = forms.ModelChoiceField(queryset=Site.objects.all(), required=False)
    group = forms.ModelChoiceField(queryset=RackGroup.objects.all(), required=False)
    u_height = forms.IntegerField(required=False, label='Height (U)')
    comments = CommentField()


def rack_site_choices():
    site_choices = Site.objects.annotate(rack_count=Count('racks'))
    return [(s.slug, u'{} ({})'.format(s.name, s.rack_count)) for s in site_choices]


def rack_group_choices():
    group_choices = RackGroup.objects.select_related('site').annotate(rack_count=Count('racks'))
    return [(g.pk, u'{} ({})'.format(g, g.rack_count)) for g in group_choices]


class RackFilterForm(forms.Form, BootstrapMixin):
    site = forms.MultipleChoiceField(required=False, choices=rack_site_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))
    group_id = forms.MultipleChoiceField(required=False, choices=rack_group_choices, label='Rack Group',
                                         widget=forms.SelectMultiple(attrs={'size': 8}))


#
# Manufacturers
#

class ManufacturerForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField()

    class Meta:
        model = Manufacturer
        fields = ['name', 'slug']


#
# Device types
#

class DeviceTypeForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField(slug_source='model')

    class Meta:
        model = DeviceType
        fields = ['manufacturer', 'model', 'slug', 'part_number', 'u_height', 'is_full_depth', 'is_console_server', 'is_pdu',
                  'is_network_device', 'subdevice_role']


class DeviceTypeBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=DeviceType.objects.all(), widget=forms.MultipleHiddenInput)
    manufacturer = forms.ModelChoiceField(queryset=Manufacturer.objects.all(), required=False)
    u_height = forms.IntegerField(min_value=1, required=False)


def devicetype_manufacturer_choices():
    manufacturer_choices = Manufacturer.objects.annotate(devicetype_count=Count('device_types'))
    return [(m.slug, u'{} ({})'.format(m.name, m.devicetype_count)) for m in manufacturer_choices]


class DeviceTypeFilterForm(forms.Form, BootstrapMixin):
    manufacturer = forms.MultipleChoiceField(required=False, choices=devicetype_manufacturer_choices,
                                             widget=forms.SelectMultiple(attrs={'size': 8}))


#
# Device component templates
#

class ConsolePortTemplateForm(forms.ModelForm, BootstrapMixin):
    name_pattern = ExpandableNameField(label='Name')

    class Meta:
        model = ConsolePortTemplate
        fields = ['name_pattern']


class ConsoleServerPortTemplateForm(forms.ModelForm, BootstrapMixin):
    name_pattern = ExpandableNameField(label='Name')

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ['name_pattern']


class PowerPortTemplateForm(forms.ModelForm, BootstrapMixin):
    name_pattern = ExpandableNameField(label='Name')

    class Meta:
        model = PowerPortTemplate
        fields = ['name_pattern']


class PowerOutletTemplateForm(forms.ModelForm, BootstrapMixin):
    name_pattern = ExpandableNameField(label='Name')

    class Meta:
        model = PowerOutletTemplate
        fields = ['name_pattern']


class InterfaceTemplateForm(forms.ModelForm, BootstrapMixin):
    name_pattern = ExpandableNameField(label='Name')

    class Meta:
        model = InterfaceTemplate
        fields = ['name_pattern', 'form_factor', 'mgmt_only']


class DeviceBayTemplateForm(forms.ModelForm, BootstrapMixin):
    name_pattern = ExpandableNameField(label='Name')

    class Meta:
        model = DeviceBayTemplate
        fields = ['name_pattern']


#
# Device roles
#

class DeviceRoleForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField()

    class Meta:
        model = DeviceRole
        fields = ['name', 'slug', 'color']


#
# Platforms
#

class PlatformForm(forms.ModelForm, BootstrapMixin):
    slug = SlugField()

    class Meta:
        model = Platform
        fields = ['name', 'slug']


#
# Devices
#

class DeviceForm(forms.ModelForm, BootstrapMixin):
    site = forms.ModelChoiceField(queryset=Site.objects.all(), widget=forms.Select(attrs={'filter-for': 'rack'}))
    rack = forms.ModelChoiceField(queryset=Rack.objects.all(), widget=APISelect(
        api_url='/api/dcim/racks/?site_id={{site}}',
        display_field='display_name',
        attrs={'filter-for': 'position'}
    ))
    position = forms.TypedChoiceField(required=False, empty_value=None,
                                      help_text="For multi-U devices, this is the lowest occupied rack unit.",
                                      widget=APISelect(api_url='/api/dcim/racks/{{rack}}/rack-units/?face={{face}}',
                                                       disabled_indicator='device'))
    manufacturer = forms.ModelChoiceField(queryset=Manufacturer.objects.all(),
                                          widget=forms.Select(attrs={'filter-for': 'device_type'}))
    device_type = forms.ModelChoiceField(queryset=DeviceType.objects.all(), label='Device type', widget=APISelect(
        api_url='/api/dcim/device-types/?manufacturer_id={{manufacturer}}',
        display_field='model'
    ))
    comments = CommentField()

    class Meta:
        model = Device
        fields = ['name', 'device_role', 'device_type', 'serial', 'site', 'rack', 'position', 'face', 'status',
                  'platform', 'primary_ip4', 'primary_ip6', 'comments']
        help_texts = {
            'device_role': "The function this device serves",
            'serial': "Chassis serial number",
        }
        widgets = {
            'face': forms.Select(attrs={'filter-for': 'position'}),
            'manufacturer': forms.Select(attrs={'filter-for': 'device_type'}),
        }

    def __init__(self, *args, **kwargs):

        super(DeviceForm, self).__init__(*args, **kwargs)

        if self.instance.pk:

            # Initialize helper selections
            self.initial['site'] = self.instance.rack.site
            self.initial['manufacturer'] = self.instance.device_type.manufacturer

            # Compile list of choices for primary IPv4 and IPv6 addresses
            for family in [4, 6]:
                ip_choices = []
                interface_ips = IPAddress.objects.filter(family=family, interface__device=self.instance)
                ip_choices += [(ip.id, u'{} ({})'.format(ip.address, ip.interface)) for ip in interface_ips]
                nat_ips = IPAddress.objects.filter(family=family, nat_inside__interface__device=self.instance)\
                    .select_related('nat_inside__interface')
                ip_choices += [(ip.id, u'{} ({} NAT)'.format(ip.address, ip.nat_inside.interface)) for ip in nat_ips]
                self.fields['primary_ip{}'.format(family)].choices = [(None, '---------')] + ip_choices

        else:

            # An object that doesn't exist yet can't have any IPs assigned to it
            self.fields['primary_ip4'].choices = []
            self.fields['primary_ip4'].widget.attrs['readonly'] = True
            self.fields['primary_ip6'].choices = []
            self.fields['primary_ip6'].widget.attrs['readonly'] = True

        # Limit rack choices
        if self.is_bound:
            self.fields['rack'].queryset = Rack.objects.filter(site__pk=self.data['site'])
        elif self.initial.get('site'):
            self.fields['rack'].queryset = Rack.objects.filter(site=self.initial['site'])
        else:
            self.fields['rack'].choices = []

        # Rack position
        pk = self.instance.pk if self.instance.pk else None
        try:
            if self.is_bound and self.data.get('rack') and str(self.data.get('face')):
                position_choices = Rack.objects.get(pk=self.data['rack'])\
                    .get_rack_units(face=self.data.get('face'), exclude=pk)
            elif self.initial.get('rack') and str(self.initial.get('face')):
                position_choices = Rack.objects.get(pk=self.initial['rack'])\
                    .get_rack_units(face=self.initial.get('face'), exclude=pk)
            else:
                position_choices = []
        except Rack.DoesNotExist:
            position_choices = []
        self.fields['position'].choices = [('', '---------')] + [
            (p['id'], {
                'label': p['name'],
                'disabled': bool(p['device'] and p['id'] != self.initial.get('position')),
            }) for p in position_choices
        ]

        # Limit device_type choices
        if self.is_bound:
            self.fields['device_type'].queryset = DeviceType.objects.filter(manufacturer__pk=self.data['manufacturer'])\
                .select_related('manufacturer')
        elif self.initial.get('manufacturer'):
            self.fields['device_type'].queryset = DeviceType.objects.filter(manufacturer=self.initial['manufacturer'])\
                .select_related('manufacturer')
        else:
            self.fields['device_type'].choices = []

        # Disable rack assignment if this is a child device installed in a parent device
        if pk and self.instance.device_type.is_child_device and hasattr(self.instance, 'parent_bay'):
            self.fields['site'].disabled = True
            self.fields['rack'].disabled = True


class BaseDeviceFromCSVForm(forms.ModelForm):
    device_role = forms.ModelChoiceField(queryset=DeviceRole.objects.all(), to_field_name='name',
                                         error_messages={'invalid_choice': 'Invalid device role.'})
    manufacturer = forms.ModelChoiceField(queryset=Manufacturer.objects.all(), to_field_name='name',
                                          error_messages={'invalid_choice': 'Invalid manufacturer.'})
    model_name = forms.CharField()
    platform = forms.ModelChoiceField(queryset=Platform.objects.all(), required=False, to_field_name='name',
                                      error_messages={'invalid_choice': 'Invalid platform.'})

    class Meta:
        fields = []
        model = Device

    def clean(self):

        manufacturer = self.cleaned_data.get('manufacturer')
        model_name = self.cleaned_data.get('model_name')

        # Validate device type
        if manufacturer and model_name:
            try:
                self.instance.device_type = DeviceType.objects.get(manufacturer=manufacturer, model=model_name)
            except DeviceType.DoesNotExist:
                self.add_error('model_name', "Invalid device type ({} {})".format(manufacturer, model_name))


class DeviceFromCSVForm(BaseDeviceFromCSVForm):
    site = forms.ModelChoiceField(queryset=Site.objects.all(), to_field_name='name', error_messages={
        'invalid_choice': 'Invalid site name.',
    })
    rack_name = forms.CharField()
    face = forms.CharField(required=False)

    class Meta(BaseDeviceFromCSVForm.Meta):
        fields = ['name', 'device_role', 'manufacturer', 'model_name', 'platform', 'serial', 'site', 'rack_name',
                  'position', 'face']

    def clean(self):

        super(DeviceFromCSVForm, self).clean()

        site = self.cleaned_data.get('site')
        rack_name = self.cleaned_data.get('rack_name')

        # Validate rack
        if site and rack_name:
            try:
                self.instance.rack = Rack.objects.get(site=site, name=rack_name)
            except Rack.DoesNotExist:
                self.add_error('rack_name', "Invalid rack ({})".format(rack_name))

    def clean_face(self):
        face = self.cleaned_data['face']
        if not face:
            return None
        try:
            return {
                'front': 0,
                'rear': 1,
            }[face.lower()]
        except KeyError:
            raise forms.ValidationError('Invalid rack face ({}); must be "front" or "rear".'.format(face))


class ChildDeviceFromCSVForm(BaseDeviceFromCSVForm):
    parent = FlexibleModelChoiceField(queryset=Device.objects.all(), to_field_name='name', required=False,
                                      error_messages={'invalid_choice': 'Parent device not found.'})
    device_bay_name = forms.CharField(required=False)

    class Meta(BaseDeviceFromCSVForm.Meta):
        fields = ['name', 'device_role', 'manufacturer', 'model_name', 'platform', 'serial', 'parent',
                  'device_bay_name']

    def clean(self):

        super(ChildDeviceFromCSVForm, self).clean()

        parent = self.cleaned_data.get('parent')
        device_bay_name = self.cleaned_data.get('device_bay_name')

        # Validate device bay
        if parent and device_bay_name:
            try:
                device_bay = DeviceBay.objects.get(device=parent, name=device_bay_name)
                if device_bay.installed_device:
                    self.add_error('device_bay_name',
                                   "Device bay ({} {}) is already occupied".format(parent, device_bay_name))
                else:
                    self.instance.parent_bay = device_bay
            except DeviceBay.DoesNotExist:
                self.add_error('device_bay_name', "Parent device/bay ({} {}) not found".format(parent, device_bay_name))


class DeviceImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=DeviceFromCSVForm)


class ChildDeviceImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=ChildDeviceFromCSVForm)


class DeviceBulkEditForm(forms.Form, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=Device.objects.all(), widget=forms.MultipleHiddenInput)
    device_type = forms.ModelChoiceField(queryset=DeviceType.objects.all(), required=False, label='Type')
    device_role = forms.ModelChoiceField(queryset=DeviceRole.objects.all(), required=False, label='Role')
    platform = forms.ModelChoiceField(queryset=Platform.objects.all(), required=False, label='Platform')
    platform_delete = forms.BooleanField(required=False, label='Set platform to "none"')
    status = forms.ChoiceField(choices=FORM_STATUS_CHOICES, required=False, initial='', label='Status')
    serial = forms.CharField(max_length=50, required=False, label='Serial Number')


def device_site_choices():
    site_choices = Site.objects.annotate(device_count=Count('racks__devices'))
    return [(s.slug, u'{} ({})'.format(s.name, s.device_count)) for s in site_choices]


def device_rack_group_choices():
    group_choices = RackGroup.objects.select_related('site').annotate(device_count=Count('racks__devices'))
    return [(g.pk, u'{} ({})'.format(g, g.device_count)) for g in group_choices]


def device_role_choices():
    role_choices = DeviceRole.objects.annotate(device_count=Count('devices'))
    return [(r.slug, u'{} ({})'.format(r.name, r.device_count)) for r in role_choices]


def device_type_choices():
    type_choices = DeviceType.objects.select_related('manufacturer').annotate(device_count=Count('instances'))
    return [(t.pk, u'{} ({})'.format(t, t.device_count)) for t in type_choices]


def device_platform_choices():
    platform_choices = Platform.objects.annotate(device_count=Count('devices'))
    return [(p.slug, u'{} ({})'.format(p.name, p.device_count)) for p in platform_choices]


class DeviceFilterForm(forms.Form, BootstrapMixin):
    site = forms.MultipleChoiceField(required=False, choices=device_site_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))
    rack_group_id = forms.MultipleChoiceField(required=False, choices=device_rack_group_choices, label='Rack Group',
                                              widget=forms.SelectMultiple(attrs={'size': 8}))
    role = forms.MultipleChoiceField(required=False, choices=device_role_choices,
                                     widget=forms.SelectMultiple(attrs={'size': 8}))
    device_type_id = forms.MultipleChoiceField(required=False, choices=device_type_choices, label='Type',
                                               widget=forms.SelectMultiple(attrs={'size': 8}))
    platform = forms.MultipleChoiceField(required=False, choices=device_platform_choices)
    status = forms.NullBooleanField(required=False, widget=forms.Select(choices=FORM_STATUS_CHOICES))


#
# Console ports
#

class ConsolePortForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = ConsolePort
        fields = ['device', 'name']
        widgets = {
            'device': forms.HiddenInput(),
        }


class ConsolePortCreateForm(forms.Form, BootstrapMixin):
    name_pattern = ExpandableNameField(label='Name')


class ConsoleConnectionCSVForm(forms.Form):
    console_server = FlexibleModelChoiceField(queryset=Device.objects.filter(device_type__is_console_server=True),
                                              to_field_name='name',
                                              error_messages={'invalid_choice': 'Console server not found'})
    cs_port = forms.CharField()
    device = FlexibleModelChoiceField(queryset=Device.objects.all(), to_field_name='name',
                                      error_messages={'invalid_choice': 'Device not found'})
    console_port = forms.CharField()
    status = forms.ChoiceField(choices=[('planned', 'Planned'), ('connected', 'Connected')])

    def clean(self):

        # Validate console server port
        if self.cleaned_data.get('console_server'):
            try:
                cs_port = ConsoleServerPort.objects.get(device=self.cleaned_data['console_server'],
                                                        name=self.cleaned_data['cs_port'])
                if ConsolePort.objects.filter(cs_port=cs_port):
                    raise forms.ValidationError("Console server port is already occupied (by {} {})"
                                                .format(cs_port.connected_console.device, cs_port.connected_console))
            except ConsoleServerPort.DoesNotExist:
                raise forms.ValidationError("Invalid console server port ({} {})"
                                            .format(self.cleaned_data['console_server'], self.cleaned_data['cs_port']))

        # Validate console port
        if self.cleaned_data.get('device'):
            try:
                console_port = ConsolePort.objects.get(device=self.cleaned_data['device'],
                                                       name=self.cleaned_data['console_port'])
                if console_port.cs_port:
                    raise forms.ValidationError("Console port is already connected (to {} {})"
                                                .format(console_port.cs_port.device, console_port.cs_port))
            except ConsolePort.DoesNotExist:
                raise forms.ValidationError("Invalid console port ({} {})"
                                            .format(self.cleaned_data['device'], self.cleaned_data['console_port']))


class ConsoleConnectionImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=ConsoleConnectionCSVForm)

    def clean(self):
        records = self.cleaned_data.get('csv')
        if not records:
            return

        connection_list = []

        for i, record in enumerate(records, start=1):
            form = self.fields['csv'].csv_form(data=record)
            if form.is_valid():
                console_port = ConsolePort.objects.get(device=form.cleaned_data['device'],
                                                       name=form.cleaned_data['console_port'])
                console_port.cs_port = ConsoleServerPort.objects.get(device=form.cleaned_data['console_server'],
                                                                     name=form.cleaned_data['cs_port'])
                if form.cleaned_data['status'] == 'planned':
                    console_port.connection_status = CONNECTION_STATUS_PLANNED
                else:
                    console_port.connection_status = CONNECTION_STATUS_CONNECTED
                connection_list.append(console_port)
            else:
                for field, errors in form.errors.items():
                    for e in errors:
                        self.add_error('csv', "Record {} {}: {}".format(i, field, e))

        self.cleaned_data['csv'] = connection_list


class ConsolePortConnectionForm(forms.ModelForm, BootstrapMixin):
    rack = forms.ModelChoiceField(queryset=Rack.objects.all(), label='Rack', required=False,
                                  widget=forms.Select(attrs={'filter-for': 'console_server'}))
    console_server = forms.ModelChoiceField(queryset=Device.objects.all(), label='Console Server', required=False,
                                            widget=APISelect(api_url='/api/dcim/devices/?rack_id={{rack}}&is_console_server=True',
                                                             attrs={'filter-for': 'cs_port'}))
    livesearch = forms.CharField(required=False, label='Console Server', widget=Livesearch(
        query_key='q', query_url='dcim-api:device_list', field_to_update='console_server')
    )
    cs_port = forms.ModelChoiceField(queryset=ConsoleServerPort.objects.all(), label='Port',
                                     widget=APISelect(api_url='/api/dcim/devices/{{console_server}}/console-server-ports/',
                                                      disabled_indicator='connected_console'))

    class Meta:
        model = ConsolePort
        fields = ['rack', 'console_server', 'livesearch', 'cs_port', 'connection_status']
        labels = {
            'cs_port': 'Port',
            'connection_status': 'Status',
        }

    def __init__(self, *args, **kwargs):

        super(ConsolePortConnectionForm, self).__init__(*args, **kwargs)

        if not self.instance.pk:
            raise RuntimeError("ConsolePortConnectionForm must be initialized with an existing ConsolePort instance.")

        self.fields['rack'].queryset = Rack.objects.filter(site=self.instance.device.rack.site)
        self.fields['cs_port'].required = True
        self.fields['connection_status'].choices = CONNECTION_STATUS_CHOICES

        # Initialize console server choices
        if self.is_bound and self.data.get('rack'):
            self.fields['console_server'].queryset = Device.objects.filter(rack=self.data['rack'], device_type__is_console_server=True)
        elif self.initial.get('rack'):
            self.fields['console_server'].queryset = Device.objects.filter(rack=self.initial['rack'], device_type__is_console_server=True)
        else:
            self.fields['console_server'].choices = []

        # Initialize CS port choices
        if self.is_bound:
            self.fields['cs_port'].queryset = ConsoleServerPort.objects.filter(device__pk=self.data['console_server'])
        elif self.initial.get('console_server', None):
            self.fields['cs_port'].queryset = ConsoleServerPort.objects.filter(device__pk=self.initial['console_server'])
        else:
            self.fields['cs_port'].choices = []


#
# Console server ports
#

class ConsoleServerPortForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = ConsoleServerPort
        fields = ['device', 'name']
        widgets = {
            'device': forms.HiddenInput(),
        }


class ConsoleServerPortCreateForm(forms.Form, BootstrapMixin):
    name_pattern = ExpandableNameField(label='Name')


class ConsoleServerPortConnectionForm(forms.Form, BootstrapMixin):
    rack = forms.ModelChoiceField(queryset=Rack.objects.all(), label='Rack', required=False,
                                  widget=forms.Select(attrs={'filter-for': 'device'}))
    device = forms.ModelChoiceField(queryset=Device.objects.all(), label='Device', required=False,
                                    widget=APISelect(api_url='/api/dcim/devices/?rack_id={{rack}}',
                                                     attrs={'filter-for': 'port'}))
    livesearch = forms.CharField(required=False, label='Device', widget=Livesearch(
        query_key='q', query_url='dcim-api:device_list', field_to_update='device')
    )
    port = forms.ModelChoiceField(queryset=ConsolePort.objects.all(), label='Port',
                                  widget=APISelect(api_url='/api/dcim/devices/{{device}}/console-ports/',
                                                   disabled_indicator='cs_port'))
    connection_status = forms.BooleanField(required=False, initial=CONNECTION_STATUS_CONNECTED, label='Status',
                                           widget=forms.Select(choices=CONNECTION_STATUS_CHOICES))

    class Meta:
        fields = ['rack', 'device', 'livesearch', 'port', 'connection_status']
        labels = {
            'connection_status': 'Status',
        }

    def __init__(self, consoleserverport, *args, **kwargs):

        super(ConsoleServerPortConnectionForm, self).__init__(*args, **kwargs)

        self.fields['rack'].queryset = Rack.objects.filter(site=consoleserverport.device.rack.site)

        # Initialize device choices
        if self.is_bound and self.data.get('rack'):
            self.fields['device'].queryset = Device.objects.filter(rack=self.data['rack'])
        elif self.initial.get('rack', None):
            self.fields['device'].queryset = Device.objects.filter(rack=self.initial['rack'])
        else:
            self.fields['device'].choices = []

        # Initialize port choices
        if self.is_bound:
            self.fields['port'].queryset = ConsolePort.objects.filter(device__pk=self.data['device'])
        elif self.initial.get('device', None):
            self.fields['port'].queryset = ConsolePort.objects.filter(device_pk=self.initial['device'])
        else:
            self.fields['port'].choices = []


#
# Power ports
#

class PowerPortForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = PowerPort
        fields = ['device', 'name']
        widgets = {
            'device': forms.HiddenInput(),
        }


class PowerPortCreateForm(forms.Form, BootstrapMixin):
    name_pattern = ExpandableNameField(label='Name')


class PowerConnectionCSVForm(forms.Form):
    pdu = FlexibleModelChoiceField(queryset=Device.objects.filter(device_type__is_pdu=True), to_field_name='name',
                                   error_messages={'invalid_choice': 'PDU not found.'})
    power_outlet = forms.CharField()
    device = FlexibleModelChoiceField(queryset=Device.objects.all(), to_field_name='name',
                                      error_messages={'invalid_choice': 'Device not found'})
    power_port = forms.CharField()
    status = forms.ChoiceField(choices=[('planned', 'Planned'), ('connected', 'Connected')])

    def clean(self):

        # Validate power outlet
        if self.cleaned_data.get('pdu'):
            try:
                power_outlet = PowerOutlet.objects.get(device=self.cleaned_data['pdu'],
                                                       name=self.cleaned_data['power_outlet'])
                if PowerPort.objects.filter(power_outlet=power_outlet):
                    raise forms.ValidationError("Power outlet is already occupied (by {} {})"
                                                .format(power_outlet.connected_port.device,
                                                        power_outlet.connected_port))
            except PowerOutlet.DoesNotExist:
                raise forms.ValidationError("Invalid PDU port ({} {})"
                                            .format(self.cleaned_data['pdu'], self.cleaned_data['power_outlet']))

        # Validate power port
        if self.cleaned_data.get('device'):
            try:
                power_port = PowerPort.objects.get(device=self.cleaned_data['device'],
                                                   name=self.cleaned_data['power_port'])
                if power_port.power_outlet:
                    raise forms.ValidationError("Power port is already connected (to {} {})"
                                                .format(power_port.power_outlet.device, power_port.power_outlet))
            except PowerPort.DoesNotExist:
                raise forms.ValidationError("Invalid power port ({} {})"
                                            .format(self.cleaned_data['device'], self.cleaned_data['power_port']))


class PowerConnectionImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=PowerConnectionCSVForm)

    def clean(self):
        records = self.cleaned_data.get('csv')
        if not records:
            return

        connection_list = []

        for i, record in enumerate(records, start=1):
            form = self.fields['csv'].csv_form(data=record)
            if form.is_valid():
                power_port = PowerPort.objects.get(device=form.cleaned_data['device'],
                                                   name=form.cleaned_data['power_port'])
                power_port.power_outlet = PowerOutlet.objects.get(device=form.cleaned_data['pdu'],
                                                                  name=form.cleaned_data['power_outlet'])
                if form.cleaned_data['status'] == 'planned':
                    power_port.connection_status = CONNECTION_STATUS_PLANNED
                else:
                    power_port.connection_status = CONNECTION_STATUS_CONNECTED
                connection_list.append(power_port)
            else:
                for field, errors in form.errors.items():
                    for e in errors:
                        self.add_error('csv', "Record {} {}: {}".format(i, field, e))

        self.cleaned_data['csv'] = connection_list


class PowerPortConnectionForm(forms.ModelForm, BootstrapMixin):
    rack = forms.ModelChoiceField(queryset=Rack.objects.all(), label='Rack', required=False,
                                  widget=forms.Select(attrs={'filter-for': 'pdu'}))
    pdu = forms.ModelChoiceField(queryset=Device.objects.all(), label='PDU', required=False,
                                 widget=APISelect(api_url='/api/dcim/devices/?rack_id={{rack}}&is_pdu=True',
                                                  attrs={'filter-for': 'power_outlet'}))
    livesearch = forms.CharField(required=False, label='PDU', widget=Livesearch(
        query_key='q', query_url='dcim-api:device_list', field_to_update='pdu')
    )
    power_outlet = forms.ModelChoiceField(queryset=PowerOutlet.objects.all(), label='Outlet',
                                          widget=APISelect(api_url='/api/dcim/devices/{{pdu}}/power-outlets/',
                                                           disabled_indicator='connected_port'))

    class Meta:
        model = PowerPort
        fields = ['rack', 'pdu', 'livesearch', 'power_outlet', 'connection_status']
        labels = {
            'power_outlet': 'Outlet',
            'connection_status': 'Status',
        }

    def __init__(self, *args, **kwargs):

        super(PowerPortConnectionForm, self).__init__(*args, **kwargs)

        if not self.instance.pk:
            raise RuntimeError("PowerPortConnectionForm must be initialized with an existing PowerPort instance.")

        self.fields['rack'].queryset = Rack.objects.filter(site=self.instance.device.rack.site)
        self.fields['power_outlet'].required = True
        self.fields['connection_status'].choices = CONNECTION_STATUS_CHOICES

        # Initialize PDU choices
        if self.is_bound and self.data.get('rack'):
            self.fields['pdu'].queryset = Device.objects.filter(rack=self.data['rack'], device_type__is_pdu=True)
        elif self.initial.get('rack', None):
            self.fields['pdu'].queryset = Device.objects.filter(rack=self.initial['rack'], device_type__is_pdu=True)
        else:
            self.fields['pdu'].choices = []

        # Initialize power outlet choices
        if self.is_bound:
            self.fields['power_outlet'].queryset = PowerOutlet.objects.filter(device__pk=self.data['pdu'])
        elif self.initial.get('pdu', None):
            self.fields['power_outlet'].queryset = PowerOutlet.objects.filter(device__pk=self.initial['pdu'])
        else:
            self.fields['power_outlet'].choices = []


#
# Power outlets
#

class PowerOutletForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = PowerOutlet
        fields = ['device', 'name']
        widgets = {
            'device': forms.HiddenInput(),
        }


class PowerOutletCreateForm(forms.Form, BootstrapMixin):
    name_pattern = ExpandableNameField(label='Name')


class PowerOutletConnectionForm(forms.Form, BootstrapMixin):
    rack = forms.ModelChoiceField(queryset=Rack.objects.all(), label='Rack', required=False,
                                  widget=forms.Select(attrs={'filter-for': 'device'}))
    device = forms.ModelChoiceField(queryset=Device.objects.all(), label='Device', required=False,
                                    widget=APISelect(api_url='/api/dcim/devices/?rack_id={{rack}}',
                                                     attrs={'filter-for': 'port'}))
    livesearch = forms.CharField(required=False, label='Device', widget=Livesearch(
        query_key='q', query_url='dcim-api:device_list', field_to_update='device')
    )
    port = forms.ModelChoiceField(queryset=PowerPort.objects.all(), label='Port',
                                  widget=APISelect(api_url='/api/dcim/devices/{{device}}/power-ports/',
                                                   disabled_indicator='power_outlet'))
    connection_status = forms.BooleanField(required=False, initial=CONNECTION_STATUS_CONNECTED, label='Status',
                                           widget=forms.Select(choices=CONNECTION_STATUS_CHOICES))

    class Meta:
        fields = ['rack', 'device', 'livesearch', 'port', 'connection_status']
        labels = {
            'connection_status': 'Status',
        }

    def __init__(self, poweroutlet, *args, **kwargs):

        super(PowerOutletConnectionForm, self).__init__(*args, **kwargs)

        self.fields['rack'].queryset = Rack.objects.filter(site=poweroutlet.device.rack.site)

        # Initialize device choices
        if self.is_bound and self.data.get('rack'):
            self.fields['device'].queryset = Device.objects.filter(rack=self.data['rack'])
        elif self.initial.get('rack', None):
            self.fields['device'].queryset = Device.objects.filter(rack=self.initial['rack'])
        else:
            self.fields['device'].choices = []

        # Initialize port choices
        if self.is_bound:
            self.fields['port'].queryset = PowerPort.objects.filter(device__pk=self.data['device'])
        elif self.initial.get('device', None):
            self.fields['port'].queryset = PowerPort.objects.filter(device_pk=self.initial['device'])
        else:
            self.fields['port'].choices = []


#
# Interfaces
#

class InterfaceForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = Interface
        fields = ['device', 'name', 'form_factor', 'mac_address', 'mgmt_only', 'description']
        widgets = {
            'device': forms.HiddenInput(),
        }


class InterfaceCreateForm(forms.ModelForm, BootstrapMixin):
    name_pattern = ExpandableNameField(label='Name')

    class Meta:
        model = Interface
        fields = ['name_pattern', 'form_factor', 'mac_address', 'mgmt_only', 'description']


class InterfaceBulkCreateForm(InterfaceCreateForm, BootstrapMixin):
    pk = forms.ModelMultipleChoiceField(queryset=Device.objects.all(), widget=forms.MultipleHiddenInput)


#
# Interface connections
#

class InterfaceConnectionForm(forms.ModelForm, BootstrapMixin):
    interface_a = forms.ChoiceField(choices=[], widget=SelectWithDisabled, label='Interface')
    rack_b = forms.ModelChoiceField(queryset=Rack.objects.all(), label='Rack', required=False,
                                    widget=forms.Select(attrs={'filter-for': 'device_b'}))
    device_b = forms.ModelChoiceField(queryset=Device.objects.all(), label='Device', required=False,
                                      widget=APISelect(api_url='/api/dcim/devices/?rack_id={{rack_b}}',
                                                       attrs={'filter-for': 'interface_b'}))
    livesearch = forms.CharField(required=False, label='Device', widget=Livesearch(
        query_key='q', query_url='dcim-api:device_list', field_to_update='device_b')
    )
    interface_b = forms.ModelChoiceField(queryset=Interface.objects.all(), label='Interface',
                                         widget=APISelect(api_url='/api/dcim/devices/{{device_b}}/interfaces/?type=physical',
                                                          disabled_indicator='is_connected'))

    class Meta:
        model = InterfaceConnection
        fields = ['interface_a', 'rack_b', 'device_b', 'interface_b', 'livesearch', 'connection_status']

    def __init__(self, device_a, *args, **kwargs):

        super(InterfaceConnectionForm, self).__init__(*args, **kwargs)

        self.fields['rack_b'].queryset = Rack.objects.filter(site=device_a.rack.site)

        # Initialize interface A choices
        device_a_interfaces = Interface.objects.filter(device=device_a).exclude(form_factor=IFACE_FF_VIRTUAL) \
            .select_related('circuit', 'connected_as_a', 'connected_as_b')
        self.fields['interface_a'].choices = [
            (iface.id, {'label': iface.name, 'disabled': iface.is_connected}) for iface in device_a_interfaces
        ]

        # Initialize device_b choices if rack_b is set
        if self.is_bound and self.data.get('rack_b'):
            self.fields['device_b'].queryset = Device.objects.filter(rack__pk=self.data['rack_b'])
        elif self.initial.get('rack_b'):
            self.fields['device_b'].queryset = Device.objects.filter(rack=self.initial['rack_b'])
        else:
            self.fields['device_b'].choices = []

        # Initialize interface_b choices if device_b is set
        if self.is_bound:
            device_b_interfaces = Interface.objects.filter(device=self.data['device_b']) \
                .exclude(form_factor=IFACE_FF_VIRTUAL).select_related('circuit', 'connected_as_a', 'connected_as_b')
        elif self.initial.get('device_b'):
            device_b_interfaces = Interface.objects.filter(device=self.initial['device_b']) \
                .exclude(form_factor=IFACE_FF_VIRTUAL).select_related('circuit', 'connected_as_a', 'connected_as_b')
        else:
            device_b_interfaces = []
        self.fields['interface_b'].choices = [
            (iface.id, {'label': iface.name, 'disabled': iface.is_connected}) for iface in device_b_interfaces
        ]


class InterfaceConnectionCSVForm(forms.Form):
    device_a = FlexibleModelChoiceField(queryset=Device.objects.all(), to_field_name='name',
                                        error_messages={'invalid_choice': 'Device A not found.'})
    interface_a = forms.CharField()
    device_b = FlexibleModelChoiceField(queryset=Device.objects.all(), to_field_name='name',
                                        error_messages={'invalid_choice': 'Device B not found.'})
    interface_b = forms.CharField()
    status = forms.ChoiceField(choices=[('planned', 'Planned'), ('connected', 'Connected')])

    def clean(self):

        # Validate interface A
        if self.cleaned_data.get('device_a'):
            try:
                interface_a = Interface.objects.get(device=self.cleaned_data['device_a'],
                                                    name=self.cleaned_data['interface_a'])
            except Interface.DoesNotExist:
                raise forms.ValidationError("Invalid interface ({} {})"
                                            .format(self.cleaned_data['device_a'], self.cleaned_data['interface_a']))
            try:
                InterfaceConnection.objects.get(Q(interface_a=interface_a) | Q(interface_b=interface_a))
                raise forms.ValidationError("{} {} is already connected"
                                            .format(self.cleaned_data['device_a'], self.cleaned_data['interface_a']))
            except InterfaceConnection.DoesNotExist:
                pass

        # Validate interface B
        if self.cleaned_data.get('device_b'):
            try:
                interface_b = Interface.objects.get(device=self.cleaned_data['device_b'],
                                                    name=self.cleaned_data['interface_b'])
            except Interface.DoesNotExist:
                raise forms.ValidationError("Invalid interface ({} {})"
                                            .format(self.cleaned_data['device_b'], self.cleaned_data['interface_b']))
            try:
                InterfaceConnection.objects.get(Q(interface_a=interface_b) | Q(interface_b=interface_b))
                raise forms.ValidationError("{} {} is already connected"
                                            .format(self.cleaned_data['device_b'], self.cleaned_data['interface_b']))
            except InterfaceConnection.DoesNotExist:
                pass


class InterfaceConnectionImportForm(BulkImportForm, BootstrapMixin):
    csv = CSVDataField(csv_form=InterfaceConnectionCSVForm)

    def clean(self):
        records = self.cleaned_data.get('csv')
        if not records:
            return

        connection_list = []
        occupied_interfaces = []

        for i, record in enumerate(records, start=1):
            form = self.fields['csv'].csv_form(data=record)
            if form.is_valid():
                interface_a = Interface.objects.get(device=form.cleaned_data['device_a'],
                                                    name=form.cleaned_data['interface_a'])
                if interface_a in occupied_interfaces:
                    raise forms.ValidationError("{} {} found in multiple connections"
                                                .format(interface_a.device.name, interface_a.name))
                interface_b = Interface.objects.get(device=form.cleaned_data['device_b'],
                                                    name=form.cleaned_data['interface_b'])
                if interface_b in occupied_interfaces:
                    raise forms.ValidationError("{} {} found in multiple connections"
                                                .format(interface_b.device.name, interface_b.name))
                connection = InterfaceConnection(interface_a=interface_a, interface_b=interface_b)
                if form.cleaned_data['status'] == 'planned':
                    connection.connection_status = CONNECTION_STATUS_PLANNED
                else:
                    connection.connection_status = CONNECTION_STATUS_CONNECTED
                connection_list.append(connection)
                occupied_interfaces.append(interface_a)
                occupied_interfaces.append(interface_b)
            else:
                for field, errors in form.errors.items():
                    for e in errors:
                        self.add_error('csv', "Record {} {}: {}".format(i, field, e))

        self.cleaned_data['csv'] = connection_list


class InterfaceConnectionDeletionForm(forms.Form, BootstrapMixin):
    confirm = forms.BooleanField(required=True)
    # Used for HTTP redirect upon successful deletion
    device = forms.ModelChoiceField(queryset=Device.objects.all(), widget=forms.HiddenInput(), required=False)


#
# Device bays
#

class DeviceBayForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = DeviceBay
        fields = ['device', 'name']
        widgets = {
            'device': forms.HiddenInput(),
        }


class DeviceBayCreateForm(forms.Form, BootstrapMixin):
    name_pattern = ExpandableNameField(label='Name')


class PopulateDeviceBayForm(forms.Form, BootstrapMixin):
    installed_device = forms.ModelChoiceField(queryset=Device.objects.all(), label='Child Device',
                                              help_text="Child devices must first be created within the rack occupied "
                                                        "by the parent device. Then they can be assigned to a bay.")

    def __init__(self, device_bay, *args, **kwargs):

        super(PopulateDeviceBayForm, self).__init__(*args, **kwargs)

        children_queryset = Device.objects.filter(rack=device_bay.device.rack,
                                                  parent_bay__isnull=True,
                                                  device_type__u_height=0,
                                                  device_type__subdevice_role=SUBDEVICE_ROLE_CHILD)\
            .exclude(pk=device_bay.device.pk)
        self.fields['installed_device'].queryset = children_queryset


#
# Connections
#

class ConsoleConnectionFilterForm(forms.Form, BootstrapMixin):
    site = forms.ModelChoiceField(required=False, queryset=Site.objects.all(), to_field_name='slug')


class PowerConnectionFilterForm(forms.Form, BootstrapMixin):
    site = forms.ModelChoiceField(required=False, queryset=Site.objects.all(), to_field_name='slug')


class InterfaceConnectionFilterForm(forms.Form, BootstrapMixin):
    site = forms.ModelChoiceField(required=False, queryset=Site.objects.all(), to_field_name='slug')


#
# IP addresses
#

class IPAddressForm(forms.ModelForm, BootstrapMixin):
    set_as_primary = forms.BooleanField(label='Set as primary IP for device', required=False)

    class Meta:
        model = IPAddress
        fields = ['address', 'vrf', 'interface', 'set_as_primary']
        help_texts = {
            'address': 'IPv4 or IPv6 address (with mask)'
        }

    def __init__(self, device, *args, **kwargs):

        super(IPAddressForm, self).__init__(*args, **kwargs)

        self.fields['vrf'].empty_label = 'Global'

        self.fields['interface'].queryset = device.interfaces.all()
        self.fields['interface'].required = True

        # If this device does not have any IP addresses assigned, default to setting the first IP as its primary
        if not IPAddress.objects.filter(interface__device=device).count():
            self.fields['set_as_primary'].initial = True


#
# Interfaces
#

class ModuleForm(forms.ModelForm, BootstrapMixin):

    class Meta:
        model = Module
        fields = ['name', 'part_id', 'serial']
