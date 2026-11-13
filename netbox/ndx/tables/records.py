import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from ndx.models import ImportRecord, Provenance
from netbox.tables import BaseTable, NetBoxTable, columns

from .template_code import PROVENANCE_SOURCE

__all__ = (
    'ImportRecordTable',
    'ProvenanceTable',
)


class ImportRecordTable(NetBoxTable):
    ndx_id = tables.Column(
        verbose_name=_('NDX ID'),
        linkify=True
    )
    object_type = columns.ContentTypeColumn(
        verbose_name=_('Object Type')
    )
    object = tables.Column(
        verbose_name=_('Object'),
        linkify=True,
        orderable=False
    )
    source = columns.ChoiceFieldColumn(
        verbose_name=_('Source')
    )
    update_available = columns.BooleanColumn(
        verbose_name=_('Update Available'),
        false_mark=None
    )
    last_imported = columns.DateTimeColumn(
        verbose_name=_('Last Imported')
    )
    actions = columns.ActionsColumn(
        actions=('delete', 'changelog')
    )

    class Meta(NetBoxTable.Meta):
        model = ImportRecord
        fields = (
            'pk', 'id', 'ndx_id', 'entry_type', 'vendor_slug', 'object_type', 'object', 'source', 'checksum',
            'update_available', 'last_imported', 'created', 'last_updated', 'actions',
        )
        default_columns = (
            'pk', 'ndx_id', 'object_type', 'object', 'source', 'update_available', 'last_imported',
        )


class ProvenanceTable(BaseTable):
    field = tables.Column(
        verbose_name=_('Field')
    )
    source = columns.TemplateColumn(
        template_code=PROVENANCE_SOURCE,
        verbose_name=_('Source')
    )
    type = tables.Column(
        verbose_name=_('Type')
    )
    confidence = tables.Column(
        verbose_name=_('Confidence')
    )
    retrieved = columns.DateColumn(
        verbose_name=_('Retrieved')
    )
    note = tables.Column(
        verbose_name=_('Note')
    )

    class Meta(BaseTable.Meta):
        model = Provenance
        fields = ('field', 'source', 'type', 'confidence', 'retrieved', 'note')
        default_columns = ('field', 'source', 'type', 'confidence', 'retrieved', 'note')
