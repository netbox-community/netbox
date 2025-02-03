from django.utils.translation import gettext_lazy as _
import django_tables2 as tables

from circuits.models import *
from tenancy.tables import ContactsColumnMixin, TenancyColumnsMixin

from netbox.tables import NetBoxTable, columns

from .columns import CommitRateColumn

__all__ = (
    'CircuitGroupAssignmentTable',
    'CircuitGroupTable',
    'CircuitTable',
    'CircuitTerminationTable',
    'CircuitTypeTable',
)


CIRCUITTERMINATION_LINK = """
{% if value.termination %}
  <a href="{{ value.termination.get_absolute_url }}">{{ value.termination }}</a>
{% endif %}
"""


class CircuitTypeTable(NetBoxTable):
    name = tables.Column(
        linkify=True,
        verbose_name=_('Name'),
    )
    color = columns.ColorColumn()
    tags = columns.TagColumn(
        url_name='circuits:circuittype_list'
    )
    circuit_count = columns.LinkedCountColumn(
        viewname='circuits:circuit_list',
        url_params={'type_id': 'pk'},
        verbose_name=_('Circuits')
    )

    class Meta(NetBoxTable.Meta):
        model = CircuitType
        fields = (
            'pk', 'id', 'name', 'circuit_count', 'color', 'description', 'slug', 'tags', 'created', 'last_updated',
            'actions',
        )
        default_columns = ('pk', 'name', 'circuit_count', 'color', 'description')


class CircuitTable(TenancyColumnsMixin, ContactsColumnMixin, NetBoxTable):
    cid = tables.Column(
        linkify=True,
        verbose_name=_('Circuit ID')
    )
    provider = tables.Column(
        verbose_name=_('Provider'),
        linkify=True
    )
    provider_account = tables.Column(
        linkify=True,
        verbose_name=_('Account')
    )
    type = tables.Column(
        verbose_name=_('Type'),
        linkify=True
    )
    status = columns.ChoiceFieldColumn()
    termination_a = columns.TemplateColumn(
        template_code=CIRCUITTERMINATION_LINK,
        orderable=False,
        verbose_name=_('Side A')
    )
    termination_z = columns.TemplateColumn(
        template_code=CIRCUITTERMINATION_LINK,
        orderable=False,
        verbose_name=_('Side Z')
    )
    commit_rate = CommitRateColumn(
        verbose_name=_('Commit Rate')
    )
    distance = columns.DistanceColumn()
    comments = columns.MarkdownColumn(
        verbose_name=_('Comments')
    )
    tags = columns.TagColumn(
        url_name='circuits:circuit_list'
    )
    assignments = columns.ManyToManyColumn(
        verbose_name=_('Assignments'),
        linkify_item=True
    )

    class Meta(NetBoxTable.Meta):
        model = Circuit
        fields = (
            'pk', 'id', 'cid', 'provider', 'provider_account', 'type', 'status', 'tenant', 'tenant_group',
            'termination_a', 'termination_z', 'install_date', 'termination_date', 'commit_rate', 'description',
            'comments', 'contacts', 'tags', 'created', 'last_updated', 'assignments',
        )
        default_columns = (
            'pk', 'cid', 'provider', 'type', 'status', 'tenant', 'termination_a', 'termination_z', 'description',
        )


class CircuitTerminationTable(NetBoxTable):
    circuit = tables.Column(
        verbose_name=_('Circuit'),
        linkify=True
    )
    provider = tables.Column(
        verbose_name=_('Provider'),
        linkify=True,
        accessor='circuit.provider'
    )
    term_side = tables.Column(
        verbose_name=_('Side')
    )
    termination_type = columns.ContentTypeColumn(
        verbose_name=_('Termination Type'),
    )
    termination = tables.Column(
        verbose_name=_('Termination Point'),
        linkify=True
    )

    # Termination types
    site = tables.Column(
        verbose_name=_('Site'),
        linkify=True,
        accessor='_site'
    )
    site_group = tables.Column(
        verbose_name=_('Site Group'),
        linkify=True,
        accessor='_sitegroup'
    )
    region = tables.Column(
        verbose_name=_('Region'),
        linkify=True,
        accessor='_region'
    )
    location = tables.Column(
        verbose_name=_('Location'),
        linkify=True,
        accessor='_location'
    )
    provider_network = tables.Column(
        verbose_name=_('Provider Network'),
        linkify=True,
        accessor='_provider_network'
    )

    class Meta(NetBoxTable.Meta):
        model = CircuitTermination
        fields = (
            'pk', 'id', 'circuit', 'provider', 'term_side', 'termination_type', 'termination', 'site_group', 'region',
            'site', 'location', 'provider_network', 'port_speed', 'upstream_speed', 'xconnect_id', 'pp_info',
            'description', 'created', 'last_updated', 'actions',
        )
        default_columns = (
            'pk', 'id', 'circuit', 'provider', 'term_side', 'termination_type', 'termination', 'description',
        )


class CircuitGroupTable(NetBoxTable):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=True
    )
    circuit_group_assignment_count = columns.LinkedCountColumn(
        viewname='circuits:circuitgroupassignment_list',
        url_params={'group_id': 'pk'},
        verbose_name=_('Circuits')
    )
    tags = columns.TagColumn(
        url_name='circuits:circuitgroup_list'
    )

    class Meta(NetBoxTable.Meta):
        model = CircuitGroup
        fields = (
            'pk', 'name', 'description', 'circuit_group_assignment_count', 'tags',
            'created', 'last_updated', 'actions',
        )
        default_columns = ('pk', 'name', 'description', 'circuit_group_assignment_count')


class CircuitGroupAssignmentTable(NetBoxTable):
    group = tables.Column(
        verbose_name=_('Group'),
        linkify=True
    )
    provider = tables.Column(
        accessor='member__provider',
        verbose_name=_('Provider'),
        linkify=True
    )
    member_type = columns.ContentTypeColumn(
        verbose_name=_('Type')
    )
    member = tables.Column(
        verbose_name=_('Circuit'),
        linkify=True
    )
    priority = tables.Column(
        verbose_name=_('Priority'),
    )
    tags = columns.TagColumn(
        url_name='circuits:circuitgroupassignment_list'
    )

    class Meta(NetBoxTable.Meta):
        model = CircuitGroupAssignment
        fields = (
            'pk', 'id', 'group', 'provider', 'member_type', 'member', 'priority', 'created', 'last_updated', 'actions',
            'tags',
        )
        default_columns = ('pk', 'group', 'provider', 'member_type', 'member', 'priority')
