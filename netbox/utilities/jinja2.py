import os

from django.apps import apps
from jinja2 import BaseLoader, TemplateNotFound

__all__ = (
    'ConfigTemplateLoader',
)


class ConfigTemplateLoader(BaseLoader):
    """
    Custom Jinja2 loader to facilitate populating template content from DataFiles.
    """
    def __init__(self, data_source):
        self.data_source = data_source

    def get_source(self, environment, template):
        DataFile = apps.get_model('core', 'DataFile')

        try:
            datafile = DataFile.objects.get(source=self.data_source, path=template)
            template_source = datafile.data_as_string
        except DataFile.DoesNotExist:
            raise TemplateNotFound(template)

        return template_source, template, True
