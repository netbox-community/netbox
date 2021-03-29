import django_tables2 as tables
from django_tables2.utils import Accessor

from dcim.models import Rack, Location, RackReservation, RackRole
from tenancy.tables import TenantColumn
from utilities.tables import (
    BaseTable, ButtonsColumn, ChoiceFieldColumn, ColorColumn, ColoredLabelColumn, LinkedCountColumn, MPTTColumn,
    TagColumn, ToggleColumn, UtilizationColumn,
)
from .template_code import LOCATION_ELEVATIONS

__all__ = (
    'RackTable',
    'RackDetailTable',
    'LocationTable',
    'RackReservationTable',
    'RackRoleTable',
)


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
    rack_count = tables.Column(
        verbose_name='Racks'
    )
    actions = ButtonsColumn(
        model=Location,
        prepend_template=LOCATION_ELEVATIONS
    )

    class Meta(BaseTable.Meta):
        model = Location
        fields = ('pk', 'name', 'site', 'rack_count', 'description', 'slug', 'actions')
        default_columns = ('pk', 'name', 'site', 'rack_count', 'description', 'actions')


#
# Rack roles
#

class RackRoleTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(linkify=True)
    rack_count = tables.Column(verbose_name='Racks')
    color = ColorColumn()
    actions = ButtonsColumn(RackRole)

    class Meta(BaseTable.Meta):
        model = RackRole
        fields = ('pk', 'name', 'rack_count', 'color', 'description', 'slug', 'actions')
        default_columns = ('pk', 'name', 'rack_count', 'color', 'description', 'actions')


#
# Racks
#

class RackTable(BaseTable):
    pk = ToggleColumn()
    name = tables.Column(
        order_by=('_name',),
        linkify=True
    )
    group = tables.Column(
        linkify=True
    )
    site = tables.Column(
        linkify=True
    )
    tenant = TenantColumn()
    status = ChoiceFieldColumn()
    role = ColoredLabelColumn()
    u_height = tables.TemplateColumn(
        template_code="{{ record.u_height }}U",
        verbose_name='Height'
    )

    class Meta(BaseTable.Meta):
        model = Rack
        fields = (
            'pk', 'name', 'site', 'group', 'status', 'facility_id', 'tenant', 'role', 'serial', 'asset_tag', 'type',
            'width', 'u_height',
        )
        default_columns = ('pk', 'name', 'site', 'group', 'status', 'facility_id', 'tenant', 'role', 'u_height')


class RackDetailTable(RackTable):
    device_count = LinkedCountColumn(
        viewname='dcim:device_list',
        url_params={'rack_id': 'pk'},
        verbose_name='Devices'
    )
    get_utilization = UtilizationColumn(
        verbose_name='Space'
    )
    get_power_utilization = UtilizationColumn(
        orderable=False,
        verbose_name='Power'
    )
    tags = TagColumn(
        url_name='dcim:rack_list'
    )

    class Meta(RackTable.Meta):
        fields = (
            'pk', 'name', 'site', 'group', 'status', 'facility_id', 'tenant', 'role', 'serial', 'asset_tag', 'type',
            'width', 'u_height', 'device_count', 'get_utilization', 'get_power_utilization', 'tags',
        )
        default_columns = (
            'pk', 'name', 'site', 'group', 'status', 'facility_id', 'tenant', 'role', 'u_height', 'device_count',
            'get_utilization', 'get_power_utilization',
        )


#
# Rack reservations
#

class RackReservationTable(BaseTable):
    pk = ToggleColumn()
    reservation = tables.Column(
        accessor='pk',
        linkify=True
    )
    site = tables.Column(
        accessor=Accessor('rack__site'),
        linkify=True
    )
    tenant = TenantColumn()
    rack = tables.Column(
        linkify=True
    )
    unit_list = tables.Column(
        orderable=False,
        verbose_name='Units'
    )
    tags = TagColumn(
        url_name='dcim:rackreservation_list'
    )
    actions = ButtonsColumn(RackReservation)

    class Meta(BaseTable.Meta):
        model = RackReservation
        fields = (
            'pk', 'reservation', 'site', 'rack', 'unit_list', 'user', 'created', 'tenant', 'description', 'tags',
            'actions',
        )
        default_columns = (
            'pk', 'reservation', 'site', 'rack', 'unit_list', 'user', 'description', 'actions',
        )
