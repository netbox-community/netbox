import fnmatch
import os

from django.apps import apps
from jinja2 import BaseLoader, TemplateNotFound
from jinja2.meta import find_referenced_templates
from jinja2.sandbox import SandboxedEnvironment

from netbox.config import get_config

__all__ = (
    'DEFAULT_JINJA2_FILTERS',
    'DataFileLoader',
    'env_filter',
    'render_jinja2',
)


def env_filter(name):
    """
    Jinja2 filter which returns the value of an environment variable, provided its name matches one of the patterns
    listed in the JINJA_ENVIRONMENT_PARAMS configuration parameter. Patterns may include wildcards. Returns None if the
    variable is not defined or its name does not match an allowed pattern.
    """
    patterns = get_config().JINJA_ENVIRONMENT_PARAMS or []
    if not any(fnmatch.fnmatchcase(name, pattern) for pattern in patterns):
        return None
    return os.environ.get(name)


DEFAULT_JINJA2_FILTERS = {
    'env': env_filter,
}


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

def render_jinja2(template_code, context, environment_params=None, data_file=None, debug=False):
    """
    Render a Jinja2 template with the provided context. Return the rendered content.

    If debug is True, the Jinja2 debug extension is enabled to assist with template development.
    """
    environment_params = dict(environment_params or {})

    if debug:
        extensions = list(environment_params.get('extensions', []))
        if 'jinja2.ext.debug' not in extensions:
            extensions.append('jinja2.ext.debug')
        environment_params['extensions'] = extensions

    if 'loader' not in environment_params:
        if data_file:
            loader = DataFileLoader(data_file.source)
            loader.cache_templates({
                data_file.path: template_code
            })
        else:
            loader = BaseLoader()
        environment_params['loader'] = loader

    # Explicitly disable autoescape after unpacking user params. Config templates render plain text
    # (network configs, scripts), not HTML. Forcing autoescape=False ensures user-supplied
    # environment_params cannot inadvertently enable it and create a latent XSS sink if output
    # is ever rendered in an HTML context.
    environment_params['autoescape'] = False
    environment = SandboxedEnvironment(**environment_params)

    # Register default filters, then apply any user-defined filters. User-defined entries take precedence so that
    # existing JINJA2_FILTERS configurations are never overridden.
    filters = {**DEFAULT_JINJA2_FILTERS, **get_config().JINJA2_FILTERS}
    environment.filters.update(filters)

    if data_file:
        template = environment.get_template(data_file.path)
    else:
        template = environment.from_string(source=template_code)
    return template.render(**context)
