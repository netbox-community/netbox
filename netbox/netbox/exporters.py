import csv
from itertools import chain

from django.core.exceptions import ImproperlyConfigured
from django.db.models import FETCH_PEERS
from django.utils.translation import gettext as _

from netbox.registry import registry
from utilities.constants import CSV_DELIMITERS, SLUG_RE

__all__ = (
    'CSVExporter',
    'Exporter',
    'YAMLExporter',
    'get_exporter',
    'get_exporters',
    'register_exporter',
)


class Exporter:
    """
    Base class for an export format offered on object list views.

    Registration instantiates the class once, and that instance serves every request, so implementations must be
    stateless.

    Attributes:
        slug: A unique identifier for this exporter (e.g. "csv"). Plugins should use a dotted namespace prefix
            (e.g. "my_plugin.xlsx").
        label: The human-friendly name shown in the UI
        content_type: The Content-Type of the HTTP response (e.g. "text/csv; charset=utf-8")
        file_extension: The extension of the downloaded file, without a leading period (e.g. "csv")
        tabular: If True, export() receives the rows of the list view's table, and the exporter is listed under both
            "Current View" and "All Data". Otherwise, it is listed under "All Data" only.
    """
    slug = None
    label = None
    content_type = None
    file_extension = None
    tabular = False

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.slug}>'

    def supports_model(self, model):
        """
        Return True if this exporter can export objects of the given model.
        """
        return True

    def export(self, *, request, queryset, headers=None, rows=None):
        """
        Return the exported data as str or bytes, or as an iterable of chunks (streamed if STREAMING_EXPORTS is
        enabled).

        Args:
            request: The current request
            queryset: The filtered queryset of objects to export, restricted to those the user can view
            headers: A list of the table's column headers (tabular exporters only)
            rows: An iterator yielding a list of cell values for each table row (tabular exporters only)
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement export()")


class _EchoBuffer:
    """
    File-like object whose write() returns the value written, so that csv.writer output can be captured line by line.
    """
    def write(self, value):
        return value


class CSVExporter(Exporter):
    slug = 'csv'
    label = 'CSV'
    content_type = 'text/csv; charset=utf-8'
    file_extension = 'csv'
    tabular = True

    def export(self, *, request, queryset, headers=None, rows=None):
        return self.write_rows(headers, rows, delimiter=self.get_delimiter(request))

    @staticmethod
    def get_delimiter(request):
        """
        Return the name of the requesting user's preferred CSV delimiter, if any.
        """
        user = getattr(request, 'user', None)
        return user.config.get('csv_delimiter') if user is not None and user.is_authenticated else None

    def write_rows(self, headers, rows, delimiter=None):
        """
        Return an iterator of CSV lines for the given headers and rows.

        Args:
            headers: A list of column headers
            rows: An iterator yielding a list of cell values for each row
            delimiter: Name of a delimiter in utilities.constants.CSV_DELIMITERS (defaults to 'comma')
        """
        if delimiter and delimiter not in CSV_DELIMITERS:
            raise ValueError(_("Invalid delimiter name: {name}").format(name=delimiter))
        writer = csv.writer(_EchoBuffer(), delimiter=CSV_DELIMITERS[delimiter or 'comma'])
        return (writer.writerow(row) for row in chain([headers], rows))


class YAMLExporter(Exporter):
    slug = 'yaml'
    label = 'YAML'
    content_type = 'text/yaml'
    file_extension = 'yaml'

    def supports_model(self, model):
        return hasattr(model, 'to_yaml')

    def export(self, *, request, queryset, headers=None, rows=None):
        # Prefetch the relations named by the model, and batch any other foreign key lookups across all objects
        queryset = queryset.prefetch_related(*getattr(queryset.model, 'yaml_prefetch', ())).fetch_mode(FETCH_PEERS)
        return '---\n'.join(obj.to_yaml() for obj in queryset)


def register_exporter(cls):
    """
    Register an Exporter subclass. Can be used as a decorator.
    """
    if not issubclass(cls, Exporter):
        raise ImproperlyConfigured(f"{cls.__name__} must be a subclass of netbox.exporters.Exporter.")
    instance = cls()
    for attr in ('slug', 'label', 'content_type', 'file_extension'):
        if not getattr(instance, attr):
            raise ImproperlyConfigured(f"{cls.__name__} must define a '{attr}' attribute.")
    if not SLUG_RE.fullmatch(instance.slug):
        raise ImproperlyConfigured(
            f"Invalid exporter slug {instance.slug!r}: must be lowercase, start with a letter, and use only letters, "
            f"digits, underscores, and dot-separated segments."
        )
    if instance.slug in registry['exporters']:
        raise ImproperlyConfigured(f"An exporter named {instance.slug} has already been registered!")
    registry['exporters'][instance.slug] = instance
    return cls


def get_exporter(slug):
    return registry['exporters'].get(slug)


def get_exporters(model):
    """
    Return all registered exporters which support the given model.
    """
    return [exporter for exporter in registry['exporters'].values() if exporter.supports_model(model)]
