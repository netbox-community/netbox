import django_tables2 as tables

from dcim.models import Location, Region, Site, SiteGroup
from netbox.tables import BaseTable, columns
from tenancy.tables import TenantColumn
from .template_code import LOCATION_BUTTONS

__all__ = (
    'LocationTable',
    'RegionTable',
    'SiteTable',
    'SiteGroupTable',
)


#
# Regions
#

class RegionTable(BaseTable):
    pk = columns.ToggleColumn()
    name = columns.MPTTColumn(
        linkify=True
    )
    site_count = columns.LinkedCountColumn(
        viewname='dcim:site_list',
        url_params={'region_id': 'pk'},
        verbose_name='Sites'
    )
    tags = columns.TagColumn(
        url_name='dcim:region_list'
    )

    class Meta(BaseTable.Meta):
        model = Region
        fields = (
            'pk', 'id', 'name', 'slug', 'site_count', 'description', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'site_count', 'description')


#
# Site groups
#

class SiteGroupTable(BaseTable):
    pk = columns.ToggleColumn()
    name = columns.MPTTColumn(
        linkify=True
    )
    site_count = columns.LinkedCountColumn(
        viewname='dcim:site_list',
        url_params={'group_id': 'pk'},
        verbose_name='Sites'
    )
    tags = columns.TagColumn(
        url_name='dcim:sitegroup_list'
    )

    class Meta(BaseTable.Meta):
        model = SiteGroup
        fields = (
            'pk', 'id', 'name', 'slug', 'site_count', 'description', 'tags', 'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'site_count', 'description')


#
# Sites
#

class SiteTable(BaseTable):
    pk = columns.ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
    region = tables.Column(
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    asn_count = columns.LinkedCountColumn(
        accessor=tables.A('asns.count'),
        viewname='ipam:asn_list',
        url_params={'site_id': 'pk'},
        verbose_name='ASNs'
    )
    tenant = TenantColumn()
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='dcim:site_list'
    )

    class Meta(BaseTable.Meta):
        model = Site
        fields = (
            'pk', 'id', 'name', 'slug', 'status', 'facility', 'region', 'group', 'tenant', 'asn_count', 'time_zone',
            'description', 'physical_address', 'shipping_address', 'latitude', 'longitude', 'comments', 'tags',
            'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'status', 'facility', 'region', 'group', 'tenant', 'description')


#
# Locations
#

class LocationTable(BaseTable):
    pk = columns.ToggleColumn()
    name = columns.MPTTColumn(
        linkify=True
    )
    site = tables.Column(
        linkify=True
    )
    tenant = TenantColumn()
    rack_count = columns.LinkedCountColumn(
        viewname='dcim:rack_list',
        url_params={'location_id': 'pk'},
        verbose_name='Racks'
    )
    device_count = columns.LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'location_id': 'pk'},
        verbose_name='Devices'
    )
    tags = columns.TagColumn(
        url_name='dcim:location_list'
    )
    actions = columns.ActionsColumn(
        extra_buttons=LOCATION_BUTTONS
    )

    class Meta(BaseTable.Meta):
        model = Location
        fields = (
            'pk', 'id', 'name', 'site', 'tenant', 'rack_count', 'device_count', 'description', 'slug', 'tags',
            'actions', 'created', 'last_updated',
        )
        default_columns = ('pk', 'name', 'site', 'tenant', 'rack_count', 'device_count', 'description')
