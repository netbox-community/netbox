import django_tables2 as tables
from django_tables2.utils import Accessor

from utilities.tables import BaseTable, ToggleColumn

from .models import (
    ConsolePort, ConsolePortTemplate, ConsoleServerPortTemplate, Device, DeviceBayTemplate, DeviceRole, DeviceType,
    Interface, InterfaceTemplate, Manufacturer, Platform, PowerOutletTemplate, PowerPort, PowerPortTemplate, Rack,
    RackGroup, Site,
)


DEVICE_LINK = """
<a href="{% url 'dcim:device' pk=record.pk %}">
    {{ record.name|default:'<span class="label label-info">Unnamed device</span>' }}
</a>
"""

RACKGROUP_EDIT_LINK = """
{% if perms.dcim.change_rackgroup %}
    <a href="{% url 'dcim:rackgroup_edit' pk=record.pk %}">Edit</a>
{% endif %}
"""

DEVICEROLE_EDIT_LINK = """
{% if perms.dcim.change_devicerole %}
    <a href="{% url 'dcim:devicerole_edit' slug=record.slug %}">Edit</a>
{% endif %}
"""

MANUFACTURER_EDIT_LINK = """
{% if perms.dcim.change_manufacturer %}
    <a href="{% url 'dcim:manufacturer_edit' slug=record.slug %}">Edit</a>
{% endif %}
"""

PLATFORM_EDIT_LINK = """
{% if perms.dcim.change_platform %}
    <a href="{% url 'dcim:platform_edit' slug=record.slug %}">Edit</a>
{% endif %}
"""

STATUS_ICON = """
{% if record.status %}
    <span class="glyphicon glyphicon-ok-sign text-success" title="Active" aria-hidden="true"></span>
{% else %}
    <span class="glyphicon glyphicon-minus-sign text-danger" title="Offline" aria-hidden="true"></span>
{% endif %}
"""


#
# Sites
#

class SiteTable(BaseTable):
    name = tables.LinkColumn('dcim:site', args=[Accessor('slug')], verbose_name='Name')
    facility = tables.Column(verbose_name='Facility')
    asn = tables.Column(verbose_name='ASN')
    rack_count = tables.Column(accessor=Accessor('count_racks'), orderable=False, verbose_name='Racks')
    device_count = tables.Column(accessor=Accessor('count_devices'), orderable=False, verbose_name='Devices')
    prefix_count = tables.Column(accessor=Accessor('count_prefixes'), orderable=False, verbose_name='Prefixes')
    vlan_count = tables.Column(accessor=Accessor('count_vlans'), orderable=False, verbose_name='VLANs')
    circuit_count = tables.Column(accessor=Accessor('count_circuits'), orderable=False, verbose_name='Circuits')

    class Meta(BaseTable.Meta):
        model = Site
        fields = ('name', 'facility', 'asn', 'rack_count', 'device_count', 'prefix_count', 'vlan_count',
                  'circuit_count')


#
# Rack groups
#

class RackGroupTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name='Name')
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')], verbose_name='Site')
    rack_count = tables.Column(verbose_name='Racks')
    slug = tables.Column(verbose_name='Slug')
    edit = tables.TemplateColumn(template_code=RACKGROUP_EDIT_LINK, verbose_name='')

    class Meta(BaseTable.Meta):
        model = RackGroup
        fields = ('pk', 'name', 'site', 'rack_count', 'slug', 'edit')


#
# Racks
#

class RackTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn('dcim:rack', args=[Accessor('pk')], verbose_name='Name')
    site = tables.LinkColumn('dcim:site', args=[Accessor('site.slug')], verbose_name='Site')
    group = tables.Column(accessor=Accessor('group.name'), verbose_name='Group')
    facility_id = tables.Column(verbose_name='Facility ID')
    u_height = tables.Column(verbose_name='Height (U)')
    devices = tables.Column(accessor=Accessor('device_count'), verbose_name='Devices')

    class Meta(BaseTable.Meta):
        model = Rack
        fields = ('pk', 'name', 'site', 'group', 'facility_id', 'u_height', 'devices')


#
# Manufacturers
#

class ManufacturerTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name='Name')
    devicetype_count = tables.Column(verbose_name='Device Types')
    slug = tables.Column(verbose_name='Slug')
    edit = tables.TemplateColumn(template_code=MANUFACTURER_EDIT_LINK, verbose_name='')

    class Meta(BaseTable.Meta):
        model = Manufacturer
        fields = ('pk', 'name', 'devicetype_count', 'slug', 'edit')


#
# Device types
#

class DeviceTypeTable(BaseTable):
    pk = ToggleColumn()
    model = tables.LinkColumn('dcim:devicetype', args=[Accessor('pk')], verbose_name='Device Type')

    class Meta(BaseTable.Meta):
        model = DeviceType
        fields = ('pk', 'model', 'manufacturer', 'u_height')


#
# Device type components
#

class ConsolePortTemplateTable(tables.Table):
    pk = ToggleColumn()

    class Meta:
        model = ConsolePortTemplate
        fields = ('pk', 'name')
        empty_text = "None"
        show_header = False
        attrs = {
            'class': 'table table-hover',
        }


class ConsoleServerPortTemplateTable(tables.Table):
    pk = ToggleColumn()

    class Meta:
        model = ConsoleServerPortTemplate
        fields = ('pk', 'name')
        empty_text = "None"
        show_header = False
        attrs = {
            'class': 'table table-hover',
        }


class PowerPortTemplateTable(tables.Table):
    pk = ToggleColumn()

    class Meta:
        model = PowerPortTemplate
        fields = ('pk', 'name')
        empty_text = "None"
        show_header = False
        attrs = {
            'class': 'table table-hover',
        }


class PowerOutletTemplateTable(tables.Table):
    pk = ToggleColumn()

    class Meta:
        model = PowerOutletTemplate
        fields = ('pk', 'name')
        empty_text = "None"
        show_header = False
        attrs = {
            'class': 'table table-hover',
        }


class InterfaceTemplateTable(tables.Table):
    pk = ToggleColumn()

    class Meta:
        model = InterfaceTemplate
        fields = ('pk', 'name')
        empty_text = "None"
        show_header = False
        attrs = {
            'class': 'table table-hover panel-body',
        }


class DeviceBayTemplateTable(tables.Table):
    pk = ToggleColumn()

    class Meta:
        model = DeviceBayTemplate
        fields = ('pk', 'name')
        empty_text = "None"
        show_header = False
        attrs = {
            'class': 'table table-hover panel-body',
        }


#
# Device roles
#

class DeviceRoleTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name='Name')
    device_count = tables.Column(verbose_name='Devices')
    slug = tables.Column(verbose_name='Slug')
    color = tables.Column(verbose_name='Color')
    edit = tables.TemplateColumn(template_code=DEVICEROLE_EDIT_LINK, verbose_name='')

    class Meta(BaseTable.Meta):
        model = DeviceRole
        fields = ('pk', 'name', 'device_count', 'slug', 'color')


#
# Platforms
#

class PlatformTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn(verbose_name='Name')
    device_count = tables.Column(verbose_name='Devices')
    slug = tables.Column(verbose_name='Slug')
    edit = tables.TemplateColumn(template_code=PLATFORM_EDIT_LINK, verbose_name='')

    class Meta(BaseTable.Meta):
        model = Platform
        fields = ('pk', 'name', 'device_count', 'slug', 'edit')


#
# Devices
#

class DeviceTable(BaseTable):
    pk = ToggleColumn()
    status = tables.TemplateColumn(template_code=STATUS_ICON, verbose_name='')
    name = tables.TemplateColumn(template_code=DEVICE_LINK, verbose_name='Name')
    site = tables.Column(accessor=Accessor('rack.site'), verbose_name='Site')
    rack = tables.LinkColumn('dcim:rack', args=[Accessor('rack.pk')], verbose_name='Rack')
    device_role = tables.Column(verbose_name='Role')
    device_type = tables.Column(verbose_name='Type')
    primary_ip = tables.TemplateColumn(orderable=False, verbose_name='IP Address',
                                       template_code="{{ record.primary_ip.address.ip }}")

    class Meta(BaseTable.Meta):
        model = Device
        fields = ('pk', 'name', 'status', 'site', 'rack', 'device_role', 'device_type', 'primary_ip')


class DeviceImportTable(BaseTable):
    name = tables.TemplateColumn(template_code=DEVICE_LINK, verbose_name='Name')
    site = tables.Column(accessor=Accessor('rack.site'), verbose_name='Site')
    rack = tables.LinkColumn('dcim:rack', args=[Accessor('rack.pk')], verbose_name='Rack')
    position = tables.Column(verbose_name='Position')
    device_role = tables.Column(verbose_name='Role')
    device_type = tables.Column(verbose_name='Type')

    class Meta(BaseTable.Meta):
        model = Device
        fields = ('name', 'site', 'rack', 'position', 'device_role', 'device_type')
        empty_text = False


#
# Device connections
#

class ConsoleConnectionTable(BaseTable):
    console_server = tables.LinkColumn('dcim:device', accessor=Accessor('cs_port.device'),
                                       args=[Accessor('cs_port.device.pk')], verbose_name='Console server')
    cs_port = tables.Column(verbose_name='Port')
    device = tables.LinkColumn('dcim:device', args=[Accessor('device.pk')], verbose_name='Device')
    name = tables.Column(verbose_name='Console port')

    class Meta(BaseTable.Meta):
        model = ConsolePort
        fields = ('console_server', 'cs_port', 'device', 'name')


class PowerConnectionTable(BaseTable):
    pdu = tables.LinkColumn('dcim:device', accessor=Accessor('power_outlet.device'),
                            args=[Accessor('power_outlet.device.pk')], verbose_name='PDU')
    power_outlet = tables.Column(verbose_name='Outlet')
    device = tables.LinkColumn('dcim:device', args=[Accessor('device.pk')], verbose_name='Device')
    name = tables.Column(verbose_name='Console port')

    class Meta(BaseTable.Meta):
        model = PowerPort
        fields = ('pdu', 'power_outlet', 'device', 'name')


class InterfaceConnectionTable(BaseTable):
    device_a = tables.LinkColumn('dcim:device', accessor=Accessor('interface_a.device'),
                                 args=[Accessor('interface_a.device.pk')], verbose_name='Device A')
    interface_a = tables.Column(verbose_name='Interface A')
    device_b = tables.LinkColumn('dcim:device', accessor=Accessor('interface_b.device'),
                                 args=[Accessor('interface_b.device.pk')], verbose_name='Device B')
    interface_b = tables.Column(verbose_name='Interface B')

    class Meta(BaseTable.Meta):
        model = Interface
        fields = ('device_a', 'interface_a', 'device_b', 'interface_b')
