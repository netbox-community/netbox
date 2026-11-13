import django_tables2 as tables
from django.contrib.contenttypes.models import ContentType
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

__all__ = (
    'ImportRecordColumn',
)


class ImportRecordColumn(tables.Column):
    """
    Display a badge linking to the NDX import record (if any) of each object.
    """
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('verbose_name', _('NDX'))
        kwargs.setdefault('accessor', tables.A('pk'))
        kwargs.setdefault('orderable', False)
        kwargs.setdefault('empty_values', ())
        super().__init__(*args, **kwargs)

    @staticmethod
    def get_import_records(table):
        """
        Return the import records of the table's objects which the requesting user may view (limited to the current
        page, if paginated), keyed by object ID. Retrieved with a single query and cached on the table.
        """
        from ndx.models import ImportRecord

        if (records := getattr(table, '_ndx_import_records', None)) is None:
            # The request is attached when the table is configured
            if (request := getattr(table, 'request', None)) is None:
                records = ImportRecord.objects.none()
            else:
                records = ImportRecord.objects.restrict(request.user, 'view')
            records = records.filter(object_type=ContentType.objects.get_for_model(table._meta.model))
            if page := getattr(table, 'page', None):
                records = records.filter(object_id__in=[row.record.pk for row in page.object_list])
            records = table._ndx_import_records = {record.object_id: record for record in records}
        return records

    def render(self, value, table):
        if (record := self.get_import_records(table).get(value)) is None:
            return ''
        if record.update_available:
            return format_html(
                '<a href="{}"><span class="badge text-bg-warning" title="{}">NDX</span></a>',
                record.get_absolute_url(), _('Update available'),
            )
        return format_html('<a href="{}"><span class="badge text-bg-blue">NDX</span></a>', record.get_absolute_url())

    def value(self, value, table):
        return 'NDX' if value in self.get_import_records(table) else ''
