from netbox.exporters import Exporter, register_exporter

__all__ = (
    'DummySiteExporter',
    'DummyTableExporter',
)


@register_exporter
class DummyTableExporter(Exporter):
    """Exports table rows as tab-separated values, encoded as bytes."""
    slug = 'dummy_plugin.tsv'
    label = 'Dummy TSV'
    content_type = 'text/tab-separated-values; charset=utf-8'
    file_extension = 'tsv'
    tabular = True

    def export(self, *, request, queryset, headers=None, rows=None):
        lines = ['\t'.join(headers), *('\t'.join('' if value is None else str(value) for value in row) for row in rows)]
        return '\n'.join(lines).encode()


@register_exporter
class DummySiteExporter(Exporter):
    """Streams the names of sites, one per line."""
    slug = 'dummy_plugin.site_names'
    label = 'Dummy Site Names'
    content_type = 'text/plain; charset=utf-8'
    file_extension = 'txt'

    def supports_model(self, model):
        return model._meta.label_lower == 'dcim.site'

    def export(self, *, request, queryset, headers=None, rows=None):
        for site in queryset:
            yield f'{site.name}\n'
