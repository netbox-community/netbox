import django_tables2 as tables

from dcim.models import Location, Region, Site, SiteGroup
from tenancy.tables import TenantColumn
from utilities.tables import (
    BaseTable, ButtonsColumn, ChoiceFieldColumn, LinkedCountColumn, MarkdownColumn, MPTTColumn, TagColumn, ToggleColumn,
)
from .template_code import LOCATION_ELEVATIONS

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
    pk = ToggleColumn()
    name = MPTTColumn(
        linkify=True
    )
    site_count = LinkedCountColumn(
        viewname='dcim:site_list',
        url_params={'region_id': 'pk'},
        verbose_name='Sites'
    )
    actions = ButtonsColumn(Region)

    class Meta(BaseTable.Meta):
        model = Region
        fields = ('pk', 'name', 'slug', 'site_count', 'description', 'actions')
        default_columns = ('pk', 'name', 'site_count', 'description', 'actions')


#
# Site groups
#

class SiteGroupTable(BaseTable):
    pk = ToggleColumn()
    name = MPTTColumn(
        linkify=True
    )
    site_count = LinkedCountColumn(
        viewname='dcim:site_list',
        url_params={'group_id': 'pk'},
        verbose_name='Sites'
    )
    actions = ButtonsColumn(SiteGroup)

    class Meta(BaseTable.Meta):
        model = SiteGroup
        fields = ('pk', 'name', 'slug', 'site_count', 'description', 'actions')
        default_columns = ('pk', 'name', 'site_count', 'description', 'actions')


#
# Sites
#

class SiteTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        linkify=True
    )
    status = ChoiceFieldColumn()
    region = tables.Column(
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    tenant = TenantColumn()
    comments = MarkdownColumn()
    tags = TagColumn(
        url_name='dcim:site_list'
    )

    class Meta(BaseTable.Meta):
        model = Site
        fields = (
            'pk', 'name', 'slug', 'status', 'facility', 'region', 'group', 'tenant', 'asn', 'time_zone', 'description',
            'physical_address', 'shipping_address', 'latitude', 'longitude', 'contact_name', 'contact_phone',
            'contact_email', 'comments', 'tags',
        )
        default_columns = ('pk', 'name', 'status', 'facility', 'region', 'group', 'tenant', 'asn', 'description')


#
# Locations
#

class LocationTable(BaseTable):
    pk = ToggleColumn()
    name = MPTTColumn(
        linkify=True
    )
    site = tables.Column(
        linkify=True
    )
    tenant = TenantColumn()
    rack_count = LinkedCountColumn(
        viewname='dcim:rack_list',
        url_params={'location_id': 'pk'},
        verbose_name='Racks'
    )
    device_count = LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'location_id': 'pk'},
        verbose_name='Devices'
    )
    actions = ButtonsColumn(
        model=Location,
        prepend_template=LOCATION_ELEVATIONS
    )

    class Meta(BaseTable.Meta):
        model = Location
        fields = ('pk', 'name', 'site', 'tenant', 'rack_count', 'device_count', 'description', 'slug', 'actions')
        default_columns = ('pk', 'name', 'site', 'tenant', 'rack_count', 'device_count', 'description', 'actions')
