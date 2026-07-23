import fnmatch
import os
import re

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
    'sanitize_http_header',
)

# Control characters (C0 range plus DEL) which are invalid in an HTTP header value. Notably, this includes the
# carriage return and line feed characters used to smuggle additional headers (CR/LF injection).
HTTP_HEADER_INVALID_CHARS_RE = re.compile(r'[\x00-\x1f\x7f]')


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


def sanitize_http_header(value):
    """
    Jinja2 filter which sanitizes a value for safe inclusion in a raw HTTP header by stripping newlines and other
    control characters. This guards against HTTP header (CR/LF) injection when interpolating untrusted data (e.g.
    user-controlled object attributes) into a webhook's additional headers.
    """
    return HTTP_HEADER_INVALID_CHARS_RE.sub('', str(value))


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

def render_jinja2(template_code, context, environment_params=None, data_file=None, debug=False, filters=None):
    """
    Render a Jinja2 template with the provided context. Return the rendered content.

    If debug is True, the Jinja2 debug extension is enabled to assist with template development.

    The optional `filters` argument is a mapping of additional Jinja2 filters to make available for this render only
    (e.g. context-specific sanitization filters). These take precedence over the default and user-configured filters.
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

    environment = SandboxedEnvironment(**environment_params)

    # Register default filters, then apply any user-defined filters. User-defined entries take precedence so that
    # existing JINJA2_FILTERS configurations are never overridden. Any filters passed for this render take precedence
    # over both so that context-specific (e.g. sanitization) filters cannot be shadowed.
    all_filters = {**DEFAULT_JINJA2_FILTERS, **get_config().JINJA2_FILTERS, **(filters or {})}
    environment.filters.update(all_filters)

    if data_file:
        template = environment.get_template(data_file.path)
    else:
        template = environment.from_string(source=template_code)
    return template.render(**context)
