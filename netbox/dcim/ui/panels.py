from django.utils.translation import gettext_lazy as _

from netbox.ui import attrs
from netbox.ui.components import ObjectPanel


class DevicePanel(ObjectPanel):
    region = attrs.NestedObjectAttr('site.region', linkify=True)
    site = attrs.ObjectAttr('site', linkify=True, grouped_by='group')
    location = attrs.NestedObjectAttr('location', linkify=True)
    rack = attrs.TemplatedAttr('rack', template_name='dcim/device/attrs/rack.html')
    virtual_chassis = attrs.NestedObjectAttr('virtual_chassis', linkify=True)
    parent_device = attrs.TemplatedAttr(
        'parent_bay',
        template_name='dcim/device/attrs/parent_device.html',
        label=_('Parent Device'),
    )
    gps_coordinates = attrs.GPSCoordinatesAttr()
    tenant = attrs.ObjectAttr('tenant', linkify=True, grouped_by='group')
    device_type = attrs.ObjectAttr('device_type', linkify=True, grouped_by='manufacturer')
    description = attrs.TextAttr('description')
    airflow = attrs.TextAttr('get_airflow_display')
    serial = attrs.TextAttr('serial', style='font-monospace')
    asset_tag = attrs.TextAttr('asset_tag', style='font-monospace')
    config_template = attrs.ObjectAttr('config_template', linkify=True)
