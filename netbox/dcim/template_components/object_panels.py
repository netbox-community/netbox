from django.utils.translation import gettext_lazy as _

from netbox.templates.components import (
    GPSCoordinatesAttr, NestedObjectAttr, ObjectAttr, ObjectDetailsPanel, TemplatedAttr, TextAttr,
)


class DevicePanel(ObjectDetailsPanel):
    region = NestedObjectAttr('site.region', linkify=True)
    site = ObjectAttr('site', linkify=True, grouped_by='group')
    location = NestedObjectAttr('location', linkify=True)
    rack = TemplatedAttr('rack', template_name='dcim/device/attrs/rack.html')
    virtual_chassis = NestedObjectAttr('virtual_chassis', linkify=True)
    parent_device = TemplatedAttr(
        'parent_bay',
        template_name='dcim/device/attrs/parent_device.html',
        label=_('Parent Device'),
    )
    gps_coordinates = GPSCoordinatesAttr()
    tenant = ObjectAttr('tenant', linkify=True, grouped_by='group')
    device_type = ObjectAttr('device_type', linkify=True, grouped_by='manufacturer')
    description = TextAttr('description')
    airflow = TextAttr('get_airflow_display')
    serial = TextAttr('serial', style='font-monospace')
    asset_tag = TextAttr('asset_tag', style='font-monospace')
    config_template = ObjectAttr('config_template', linkify=True)
