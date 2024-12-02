from django.apps import apps
from jinja2 import BaseLoader, TemplateNotFound
from jinja2.meta import find_referenced_templates
from jinja2.sandbox import SandboxedEnvironment

from netbox.config import get_config

__all__ = (
    'DataFileLoader',
)


class DataFileLoader(BaseLoader):
    """
    Custom Jinja2 loader to facilitate populating template content from DataFiles.
    """
    def __init__(self, data_source):
        self.data_source = data_source
        self._template_cache = {}

    def get_source(self, environment, template):
        DataFile = apps.get_model('core', 'DataFile')

        # Retrieve template content from cache
        try:
            template_source = self._template_cache[template]
        except KeyError:
            raise TemplateNotFound(template)

        # Find and pre-fetch referenced templates
        if referenced_templates := tuple(find_referenced_templates(environment.parse(template_source))):
            related_files = DataFile.objects.filter(source=self.data_source)
            # None indicates the use of dynamic resolution. If dependent files are statically
            # defined, we can filter by path for optimization.
            if None not in referenced_templates:
                related_files = related_files.filter(path__in=referenced_templates)
            self.cache_templates({
                df.path: df.data_as_string for df in related_files
            })

        return template_source, template, lambda: True

    def cache_templates(self, templates):
        self._template_cache.update(templates)


#
# Utility functions
#

def render_jinja2(template_code, context):
    """
    Render a Jinja2 template with the provided context. Return the rendered content.
    """
    environment = SandboxedEnvironment()
    environment.filters.update(get_config().JINJA2_FILTERS)
    return environment.from_string(source=template_code).render(**context)
