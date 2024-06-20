from django.utils.translation import gettext_lazy as _
import django_tables2 as tables
from django_tables2.utils import Accessor
from django.utils.safestring import mark_safe

from dcim.models import Cable
from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenancyColumnsMixin
from .template_code import CABLE_LENGTH

__all__ = (
    'CableTable',
)


class CableTerminationsColumn(tables.Column):
    """
    Args:
        cable_end: Which side of the cable to report on (A or B)
        attr: The CableTermination attribute to return for each instance (returns the termination object by default)
    """
    def __init__(self, cable_end, attr='termination', *args, **kwargs):
        self.cable_end = cable_end
        self.attr = attr
        super().__init__(accessor=Accessor('terminations'), *args, **kwargs)

    def _get_terminations(self, manager):
        terminations = set()
        for cabletermination in manager.all():
            if cabletermination.cable_end == self.cable_end:
                if termination := getattr(cabletermination, self.attr, None):
                    terminations.add(termination)

        return terminations

    def render(self, value):
        links = [
            f'<a href="{term.get_absolute_url()}">{term}</a>' for term in self._get_terminations(value)
        ]
        return mark_safe('<br />'.join(links) or '&mdash;')

    def value(self, value):
        return ','.join([str(t) for t in self._get_terminations(value)])


#
# Cables
#

class CableTable(TenancyColumnsMixin, NetBoxTable):
    a_terminations = CableTerminationsColumn(
        cable_end='A',
        orderable=False,
        verbose_name=_('Termination A')
    )
    b_terminations = CableTerminationsColumn(
        cable_end='B',
        orderable=False,
        verbose_name=_('Termination B')
    )
    device_a = CableTerminationsColumn(
        cable_end='A',
        attr='_device',
        orderable=False,
        verbose_name=_('Device A')
    )
    device_b = CableTerminationsColumn(
        cable_end='B',
        attr='_device',
        orderable=False,
        verbose_name=_('Device B')
    )
    location_a = CableTerminationsColumn(
        cable_end='A',
        attr='_location',
        orderable=False,
        verbose_name=_('Location A')
    )
    location_b = CableTerminationsColumn(
        cable_end='B',
        attr='_location',
        orderable=False,
        verbose_name=_('Location B')
    )
    rack_a = CableTerminationsColumn(
        cable_end='A',
        attr='_rack',
        orderable=False,
        verbose_name=_('Rack A')
    )
    rack_b = CableTerminationsColumn(
        cable_end='B',
        attr='_rack',
        orderable=False,
        verbose_name=_('Rack B')
    )
    site_a = CableTerminationsColumn(
        cable_end='A',
        attr='_site',
        orderable=False,
        verbose_name=_('Site A')
    )
    site_b = CableTerminationsColumn(
        cable_end='B',
        attr='_site',
        orderable=False,
        verbose_name=_('Site B')
    )
    status = columns.ChoiceFieldColumn()
    length = columns.TemplateColumn(
        template_code=CABLE_LENGTH,
        order_by=('_abs_length')
    )
    color = columns.ColorColumn()
    comments = columns.MarkdownColumn()
    tags = columns.TagColumn(
        url_name='dcim:cable_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Cable
        fields = (
            'pk', 'id', 'label', 'a_terminations', 'b_terminations', 'device_a', 'device_b', 'rack_a', 'rack_b',
            'location_a', 'location_b', 'site_a', 'site_b', 'status', 'type', 'tenant', 'tenant_group', 'color',
            'length', 'description', 'comments', 'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'id', 'label', 'a_terminations', 'b_terminations', 'status', 'type',
        )
