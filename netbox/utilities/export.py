from django.utils.translation import gettext_lazy as _
from django_tables2.export import TableExport as TableExport_

from utilities.constants import CSV_DELIMITERS

__all__ = (
    'TableExport',
)


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
