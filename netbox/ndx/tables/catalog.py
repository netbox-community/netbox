import django_tables2 as tables
from django.utils.translation import gettext_lazy as _

from netbox.tables import BaseTable, columns

from .template_code import CATALOG_ENRICHMENT, CATALOG_ENTRY_LINK, CATALOG_IMPORTED, CATALOG_SOURCE

__all__ = (
    'CatalogEntryTable',
)


class CatalogEntryTable(BaseTable):
    """
    Entries retrieved from the NDX catalog.
    """
    pk = columns.ToggleColumn(
        accessor=tables.A('ndx_id'),
        visible=True
    )
    model = columns.TemplateColumn(
        template_code=CATALOG_ENTRY_LINK,
        verbose_name=_('Model')
    )
    manufacturer = tables.Column(
        verbose_name=_('Manufacturer')
    )
    part_number = tables.Column(
        verbose_name=_('Part Number')
    )
    type = tables.Column(
        verbose_name=_('Type')
    )
    source = columns.TemplateColumn(
        template_code=CATALOG_SOURCE,
        verbose_name=_('Source')
    )
    enrichment = columns.TemplateColumn(
        accessor=tables.A('enrichment_flags'),
        template_code=CATALOG_ENRICHMENT,
        verbose_name=_('Enrichment')
    )
    imported = columns.TemplateColumn(
        accessor=tables.A('import_record'),
        template_code=CATALOG_IMPORTED,
        verbose_name=_('Imported')
    )

    exempt_columns = ('pk',)

    class Meta(BaseTable.Meta):
        empty_text = _('No catalog entries found')
        fields = (
            'pk', 'model', 'manufacturer', 'part_number', 'type', 'source', 'enrichment', 'imported',
        )
        default_columns = (
            'pk', 'model', 'manufacturer', 'part_number', 'type', 'source', 'enrichment', 'imported',
        )
        orderable = False
