import django_tables2 as tables
from django_tables2.utils import Accessor

from dcim.models import Cable
from utilities.tables import BaseTable, ChoiceFieldColumn, ColorColumn, TagColumn, ToggleColumn
from .template_code import CABLE_LENGTH, CABLE_TERMINATION_PARENT

__all__ = (
    'CableTable',
)


#
# Cables
#

class CableTable(BaseTable):
    pk = ToggleColumn()
    id = tables.Column(
        linkify=True,
        verbose_name='ID'
    )
    termination_a_parent = tables.TemplateColumn(
        template_code=CABLE_TERMINATION_PARENT,
        accessor=Accessor('termination_a'),
        orderable=False,
        verbose_name='Side A'
    )
    termination_a = tables.LinkColumn(
        accessor=Accessor('termination_a'),
        orderable=False,
        verbose_name='Termination A'
    )
    termination_b_parent = tables.TemplateColumn(
        template_code=CABLE_TERMINATION_PARENT,
        accessor=Accessor('termination_b'),
        orderable=False,
        verbose_name='Side B'
    )
    termination_b = tables.LinkColumn(
        accessor=Accessor('termination_b'),
        orderable=False,
        verbose_name='Termination B'
    )
    status = ChoiceFieldColumn()
    length = tables.TemplateColumn(
        template_code=CABLE_LENGTH,
        order_by='_abs_length'
    )
    color = ColorColumn()
    tags = TagColumn(
        url_name='dcim:cable_list'
    )

    class Meta(BaseTable.Meta):
        model = Cable
        fields = (
            'pk', 'id', 'label', 'termination_a_parent', 'termination_a', 'termination_b_parent', 'termination_b',
            'status', 'type', 'color', 'length', 'tags',
        )
        default_columns = (
            'pk', 'id', 'label', 'termination_a_parent', 'termination_a', 'termination_b_parent', 'termination_b',
            'status', 'type',
        )
