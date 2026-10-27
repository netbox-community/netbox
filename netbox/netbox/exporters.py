import csv
import re
from itertools import chain

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db.models import FETCH_PEERS
from django.utils.translation import gettext as _

from netbox.registry import registry
from utilities.constants import CSV_DELIMITERS

__all__ = (
    'CSVExporter',
    'Exporter',
    'TableExporter',
    'YAMLExporter',
    'get_exporter',
    'get_exporters',
    'register_exporter',
)

SLUG_RE = re.compile(r'^[a-z][a-z0-9_]*(\.[a-z0-9_]+)*$')


class Exporter:
    """
    Base class for an export format offered on object list views. Exporters are listed under "All Data" only.

    Registration instantiates the class once, and that instance serves every request, so implementations must be
    stateless.

    Attributes:
        slug: A unique identifier for this exporter (e.g. "csv"). Plugins should use a dotted namespace prefix
            (e.g. "my_plugin.xlsx").
        label: The human-friendly name shown in the UI
        content_type: The Content-Type of the HTTP response (e.g. "text/csv; charset=utf-8")
        file_extension: The extension of the downloaded file, without a leading period (e.g. "csv")
    """
    slug = None
    label = None
    content_type = None
    file_extension = None

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.slug}>'

    def supports_model(self, model):
        """
        Return True if this exporter can export objects of the given model.
        """
        return True

    def export(self, *, request, queryset):
        """
        Return the exported data as str or bytes, or as an iterable of chunks to stream the response.

        Args:
            request: The current request
            queryset: The filtered queryset of objects to export, restricted to those the user can view
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement export()")


class TableExporter(Exporter):
    """
    An exporter which renders the rows of an object list table. Table exporters are listed under both "Current View"
    and "All Data".
    """
    def export_rows(self, *, request, headers, rows):
        """
        Return the exported data (as for export()) given a list of column headers and an iterator of row values.

        Args:
            request: The current request
            headers: A list of column headers
            rows: An iterator yielding a list of cell values for each row
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement export_rows()")


class _EchoBuffer:
    """
    File-like object whose write() returns the value written, so that csv.writer output can be captured line by line.
    """
    def write(self, value):
        return value


class CSVExporter(TableExporter):
    slug = 'csv'
    label = 'CSV'
    content_type = 'text/csv; charset=utf-8'
    file_extension = 'csv'

    def export_rows(self, *, request, headers, rows):
        delimiter = request.user.config.get('csv_delimiter') if request.user.is_authenticated else None
        return self.write_rows(headers, rows, delimiter=delimiter)

    def write_rows(self, headers, rows, delimiter=None):
        """
        Return the given headers and rows as CSV, either as a string or (if STREAMING_EXPORTS is enabled) as an
        iterator of lines.

        Args:
            headers: A list of column headers
            rows: An iterator yielding a list of cell values for each row
            delimiter: Name of a delimiter in utilities.constants.CSV_DELIMITERS (defaults to 'comma')
        """
        if delimiter and delimiter not in CSV_DELIMITERS:
            raise ValueError(_("Invalid delimiter name: {name}").format(name=delimiter))
        writer = csv.writer(_EchoBuffer(), delimiter=CSV_DELIMITERS[delimiter or 'comma'])
        lines = (writer.writerow(row) for row in chain([headers], rows))
        if settings.STREAMING_EXPORTS:
            return lines
        return ''.join(lines)


class YAMLExporter(Exporter):
    slug = 'yaml'
    label = 'YAML'
    content_type = 'text/yaml'
    file_extension = 'yaml'

    def supports_model(self, model):
        return hasattr(model, 'to_yaml')

    def export(self, *, request, queryset):
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
