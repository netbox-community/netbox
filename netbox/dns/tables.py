import django_tables2 as tables
from django_tables2.utils import Accessor

from utilities.tables import BaseTable, ToggleColumn

from ipam.models import IPAddress
from .models import Zone, Record

#
# Zones
#


class ZoneTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn('dns:zone', args=[Accessor('pk')], verbose_name='Name')
    record_count = tables.Column(verbose_name='Records')
    ttl = tables.Column(verbose_name='TTL')
    soa_name = tables.Column(verbose_name='SOA Name')
    soa_contact = tables.Column(verbose_name='SOA Contact')
    soa_serial = tables.Column(verbose_name='SOA Serial')

    class Meta(BaseTable.Meta):
        model = Zone
        fields = ('pk', 'name', 'ttl', 'soa_name', 'soa_contact', 'soa_serial')


#
# Records
#


class RecordTable(BaseTable):
    pk = ToggleColumn()
    name = tables.LinkColumn('dns:record', args=[Accessor('pk')], verbose_name='Name')
    record_type = tables.Column(verbose_name='Type')
    priority = tables.Column(verbose_name='Priority')
    address = tables.LinkColumn('ipam:ipaddress', args=[Accessor('address.pk')], verbose_name='IP Address')
    value = tables.Column(verbose_name='Text Value')
    zone = tables.LinkColumn('dns:zone', args=[Accessor('zone.pk')], verbose_name='Zone')

    class Meta(BaseTable.Meta):
        model = Record
        fields = ('pk', 'name', 'record_type', 'priority', 'address', 'value')


class RecordBriefTable(BaseTable):
    name = tables.LinkColumn('dns:record', args=[Accessor('pk')], verbose_name='Name')
    record_type = tables.Column(verbose_name='Type')
    priority = tables.Column(verbose_name='Priority')
    zone = tables.LinkColumn('dns:zone', args=[Accessor('zone.pk')], verbose_name='Zone')

    class Meta(BaseTable.Meta):
        model = Record
        fields = ('name', 'record_type', 'priority', 'zone')


class RecordZoneTable(BaseTable):
    name = tables.LinkColumn('dns:record', args=[Accessor('pk')], verbose_name='Name')
    record_type = tables.Column(verbose_name='Type')
    priority = tables.Column(verbose_name='Priority')
    address = tables.LinkColumn('ipam:ipaddress', args=[Accessor('address.pk')], verbose_name='IP Address')
    value = tables.Column(verbose_name='Value')

    class Meta(BaseTable.Meta):
        model = Record
        fields = ('name', 'record_type', 'priority', 'address', 'value')
