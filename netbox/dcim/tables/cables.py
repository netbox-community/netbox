import django_tables2 as tables
from django_tables2.utils import Accessor

from dcim.models import Cable
from netbox.tables import NetBoxTable, columns
from tenancy.tables import TenantColumn
from .template_code import CABLE_LENGTH

__all__ = (
    'CableTable',
)


class CableTerminationColumn(tables.TemplateColumn):

    def __init__(self, cable_end, *args, **kwargs):
        template_code = """
        {% for term in value.all %}
          {% if term.cable_end == '""" + cable_end + """' %}
            <a href="{{ term.termination.get_absolute_url }}">{{ term.termination }}</a>
          {% endif %}
        {% endfor %}
        """
        super().__init__(template_code=template_code, *args, **kwargs)

    def value(self, value):
        return ', '.join(value.all())


#
# Cables
#

class CableTable(NetBoxTable):
    # termination_a_parent = tables.TemplateColumn(
    #     template_code=CABLE_TERMINATION_PARENT,
    #     accessor=Accessor('termination_a'),
    #     orderable=False,
    #     verbose_name='Side A'
    # )
    # rack_a = tables.Column(
    #     accessor=Accessor('termination_a__device__rack'),
    #     orderable=False,
    #     linkify=True,
    #     verbose_name='Rack A'
    # )
    # termination_b_parent = tables.TemplateColumn(
    #     template_code=CABLE_TERMINATION_PARENT,
    #     accessor=Accessor('termination_b'),
    #     orderable=False,
    #     verbose_name='Side B'
    # )
    # rack_b = tables.Column(
    #     accessor=Accessor('termination_b__device__rack'),
    #     orderable=False,
    #     linkify=True,
    #     verbose_name='Rack B'
    # )
    a_terminations = CableTerminationColumn(
        cable_end='A',
        accessor=Accessor('terminations'),
        orderable=False
    )
    b_terminations = CableTerminationColumn(
        cable_end='B',
        accessor=Accessor('terminations'),
        orderable=False
    )
    status = columns.ChoiceFieldColumn()
    tenant = TenantColumn()
    length = columns.TemplateColumn(
        template_code=CABLE_LENGTH,
        order_by=('_abs_length', 'length_unit')
    )
    color = columns.ColorColumn()
    tags = columns.TagColumn(
        url_name='dcim:cable_list'
    )

    class Meta(NetBoxTable.Meta):
        model = Cable
        fields = (
            'pk', 'id', 'label', 'a_terminations', 'b_terminations', 'status', 'type', 'tenant', 'color', 'length',
            'tags', 'created', 'last_updated',
        )
        default_columns = (
            'pk', 'id', 'label', 'a_terminations', 'b_terminations', 'status', 'type',
        )
