from django.utils.translation import gettext_lazy as _
import django_tables2 as tables

from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin
from wireless.models import *
from .template_code import WIRELESS_LINK_DISTANCE

__all__ = (
    'WirelessLinkTable',
)


class WirelessLinkTable(TenancyColumnsMixin, NetBoxTable):
    id = tables.Column(
        linkify=True,
        verbose_name=_('ID')
    )
    status = columns.ChoiceFieldColumn(
        verbose_name=_('Status'),
    )
    device_a = tables.Column(
        verbose_name=_('Device A'),
        accessor=tables.A('interface_a__device'),
        linkify=True
    )
    interface_a = tables.Column(
        verbose_name=_('Interface A'),
        linkify=True
    )
    device_b = tables.Column(
        verbose_name=_('Device B'),
        accessor=tables.A('interface_b__device'),
        linkify=True
    )
    interface_b = tables.Column(
        verbose_name=_('Interface B'),
        linkify=True
    )
    distance = columns.TemplateColumn(
        template_code=WIRELESS_LINK_DISTANCE,
        order_by=('_abs_distance')
    )
    tags = columns.TagColumn(
        url_name='wireless:wirelesslink_list'
    )

    class Meta(NetBoxTable.Meta):
        model = WirelessLink
        fields = (
            'pk', 'id', 'status', 'device_a', 'interface_a', 'device_b', 'interface_b', 'ssid', 'tenant',
            'tenant_group', 'distance', 'description', 'auth_type', 'auth_cipher', 'auth_psk', 'tags',
            'created', 'last_updated',
        )
        default_columns = (
            'pk', 'id', 'status', 'device_a', 'interface_a', 'device_b', 'interface_b', 'ssid', 'auth_type',
            'description',
        )
