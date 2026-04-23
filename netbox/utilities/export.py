import csv

from django.http import StreamingHttpResponse
from django.utils.encoding import force_str
from django.utils.translation import gettext_lazy as _
from django_tables2.data import TableQuerysetData
from django_tables2.export import TableExport as TableExport_
from django_tables2.rows import BoundRow

from utilities.constants import CSV_DELIMITERS

__all__ = (
    'TableExport',
    'stream_table_csv_response',
)

EXPORT_CHUNK_SIZE = 1000


class TableExport(TableExport_):
    """
    A subclass of django-tables2's TableExport class which allows us to specify a delimiting
    characters for CSV exports.
    """
    def __init__(self, *args, delimiter=None, **kwargs):
        if delimiter and delimiter not in CSV_DELIMITERS.keys():
            raise ValueError(_("Invalid delimiter name: {name}").format(name=delimiter))
        self.delimiter = delimiter or 'comma'
        super().__init__(*args, **kwargs)

    def export(self):
        if self.format == self.CSV and self.delimiter is not None:
            delimiter = CSV_DELIMITERS[self.delimiter]
            return self.dataset.export(self.format, delimiter=delimiter)
        return super().export()


class _EchoBuffer:
    """
    File-like object whose write() simply returns the value written, so csv.writer output can be
    captured row-by-row and fed to a StreamingHttpResponse.
    """
    def write(self, value):
        return value


def stream_table_csv_response(table, exclude_columns=None, filename=None, delimiter=None):
    """
    Return a StreamingHttpResponse that emits the given table's rows as CSV without first buffering
    the entire dataset in memory. Queryset-backed tables are iterated in chunks using
    QuerySet.iterator() to cap peak memory; prefetched relations are preserved under Django 4.1+.

    Args:
        table: The django-tables2 Table instance to export
        exclude_columns: Iterable of column names to omit from the export
        filename: If set, a Content-Disposition header is included in the HTTP response, indicating its treatment
            as a file attachment with the specified name.
        delimiter: Name of a delimiter in utilities.constants.CSV_DELIMITERS (defaults to 'comma')
    """
    if delimiter and delimiter not in CSV_DELIMITERS:
        raise ValueError(_("Invalid delimiter name: {name}").format(name=delimiter))
    csv_delimiter = CSV_DELIMITERS[delimiter or 'comma']
    exclude_columns = exclude_columns or set()

    columns = [
        column for column in table.columns.iterall()
        if not (column.column.exclude_from_export or column.name in exclude_columns)
    ]

    writer = csv.writer(_EchoBuffer(), delimiter=csv_delimiter)

    def iter_records():
        if isinstance(table.data, TableQuerysetData):
            yield from table.data.data.iterator(chunk_size=EXPORT_CHUNK_SIZE)
        else:
            yield from table.data

    def row_generator():
        yield writer.writerow([
            force_str(column.header, strings_only=True) for column in columns
        ])
        for record in iter_records():
            row = BoundRow(record, table=table)
            yield writer.writerow([
                force_str(row.get_cell_value(column.name), strings_only=True)
                for column in columns
            ])

    response = StreamingHttpResponse(row_generator(), content_type='text/csv; charset=utf-8')
    if filename is not None:
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
