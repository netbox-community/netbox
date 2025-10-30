from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs
from netbox.ui.components import ObjectPanel


class DevicePanel(ObjectPanel):
    region = attrs.NestedObjectAttr('site.region', label=_('Region'), linkify=True)
    site = attrs.ObjectAttr('site', label=_('Site'), linkify=True, grouped_by='group')
    location = attrs.NestedObjectAttr('location', label=_('Location'), linkify=True)
    rack = attrs.TemplatedAttr('rack', label=_('Rack'), template_name='dcim/device/attrs/rack.html')
    virtual_chassis = attrs.NestedObjectAttr('virtual_chassis', label=_('Virtual chassis'), linkify=True)
    parent_device = attrs.TemplatedAttr(
        'parent_bay',
        label=_('Parent device'),
        template_name='dcim/device/attrs/parent_device.html',
    )
    gps_coordinates = attrs.GPSCoordinatesAttr()
    tenant = attrs.ObjectAttr('tenant', label=_('Tenant'), linkify=True, grouped_by='group')
    device_type = attrs.ObjectAttr('device_type', label=_('Device type'), linkify=True, grouped_by='manufacturer')
    description = attrs.TextAttr('description', label=_('Description'))
    airflow = attrs.ChoiceAttr('airflow', label=_('Airflow'))
    serial = attrs.TextAttr('serial', label=_('Serial number'), style='font-monospace', copy_button=True)
    asset_tag = attrs.TextAttr('asset_tag', label=_('Asset tag'), style='font-monospace', copy_button=True)
    config_template = attrs.ObjectAttr('config_template', label=_('Config template'), linkify=True)


class DeviceManagementPanel(ObjectPanel):
    status = attrs.ChoiceAttr('status', label=_('Status'))
    role = attrs.NestedObjectAttr('role', label=_('Role'), linkify=True, max_depth=3)
    platform = attrs.NestedObjectAttr('platform', label=_('Platform'), linkify=True, max_depth=3)
    primary_ip4 = attrs.TemplatedAttr(
        'primary_ip4',
        label=_('Primary IPv4'),
        template_name='dcim/device/attrs/ipaddress.html',
    )
    primary_ip6 = attrs.TemplatedAttr(
        'primary_ip6',
        label=_('Primary IPv6'),
        template_name='dcim/device/attrs/ipaddress.html',
    )
    oob_ip = attrs.TemplatedAttr(
        'oob_ip',
        label=_('Out-of-band IP'),
        template_name='dcim/device/attrs/ipaddress.html',
    )


class SitePanel(ObjectPanel):
    region = attrs.NestedObjectAttr('region', label=_('Region'), linkify=True)
    group = attrs.NestedObjectAttr('group', label=_('Group'), linkify=True)
    status = attrs.ChoiceAttr('status', label=_('Status'))
    tenant = attrs.ObjectAttr('tenant', label=_('Tenant'), linkify=True, grouped_by='group')
    facility = attrs.TextAttr('facility', label=_('Facility'))
    description = attrs.TextAttr('description', label=_('Description'))
    timezone = attrs.TimezoneAttr('time_zone', label=_('Timezone'))
    physical_address = attrs.AddressAttr('physical_address', label=_('Physical address'), map_url=True)
    shipping_address = attrs.AddressAttr('shipping_address', label=_('Shipping address'), map_url=True)
    gps_coordinates = attrs.GPSCoordinatesAttr()
