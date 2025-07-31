import importlib.abc
import importlib.util
import os
import sys

from django.core.files.storage import storages
from django.db import models
from django.http import HttpResponse
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _

from extras.constants import DEFAULT_MIME_TYPE, JINJA_ENV_PARAMS_WITH_PATH_IMPORT
from extras.utils import filename_from_model, filename_from_object
from utilities.jinja2 import render_jinja2

__all__ = (
    'PythonModuleMixin',
    'RenderTemplateMixin',
)


class CustomStoragesLoader(importlib.abc.Loader):
    """
    Custom loader for exec_module to use django-storages instead of the file system.
    """
    def __init__(self, filename):
        self.filename = filename

    def create_module(self, spec):
        return None  # Use default module creation

    def exec_module(self, module):
        storage = storages.create_storage(storages.backends["scripts"])
        with storage.open(self.filename, 'rb') as f:
            code = f.read()
        exec(code, module.__dict__)


class PythonModuleMixin:

    def get_jobs(self, name):
        """
        Returns a list of Jobs associated with this specific script or report module
        :param name: The class name of the script or report
        :return: List of Jobs associated with this
        """
        return self.jobs.filter(
            name=name
        )

    @property
    def path(self):
        return os.path.splitext(self.file_path)[0]

    @property
    def python_name(self):
        path, filename = os.path.split(self.full_path)
        name = os.path.splitext(filename)[0]
        if name == '__init__':
            # File is a package
            return os.path.basename(path)
        else:
            return name

    def get_module(self):
        """
        Load the module using importlib, but use a custom loader to use django-storages
        instead of the file system.
        """
        spec = importlib.util.spec_from_file_location(self.python_name, self.name)
        if spec is None:
            raise ModuleNotFoundError(f"Could not find module: {self.python_name}")
        loader = CustomStoragesLoader(self.name)
        module = importlib.util.module_from_spec(spec)
        sys.modules[self.python_name] = module
        loader.exec_module(module)

        return module


class RenderTemplateMixin(models.Model):
    """
    Enables support for rendering templates.
    """
    template_code = models.TextField(
        verbose_name=_('template code'),
        help_text=_('Jinja template code.')
    )
    environment_params = models.JSONField(
        verbose_name=_('environment parameters'),
        blank=True,
        null=True,
        default=dict,
        help_text=_(
            'Any <a href="{url}">additional parameters</a> to pass when constructing the Jinja environment'
        ).format(url='https://jinja.palletsprojects.com/en/stable/api/#jinja2.Environment')
    )
    mime_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name=_('MIME type'),
        help_text=_('Defaults to <code>{default}</code>').format(default=DEFAULT_MIME_TYPE),
    )
    file_name = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Filename to give to the rendered export file')
    )
    file_extension = models.CharField(
        verbose_name=_('file extension'),
        max_length=15,
        blank=True,
        help_text=_('Extension to append to the rendered filename')
    )
    as_attachment = models.BooleanField(
        verbose_name=_('as attachment'),
        default=True,
        help_text=_("Download file as attachment")
    )

    class Meta:
        abstract = True

    def get_context(self, context=None, queryset=None):
        raise NotImplementedError(_("{class_name} must implement a get_context() method.").format(
            class_name=self.__class__
        ))

    def get_environment_params(self):
        """
        Pre-processing of any defined Jinja environment parameters (e.g. to support path resolution).
        """
        params = self.environment_params or {}
        for name, value in params.items():
            if name in JINJA_ENV_PARAMS_WITH_PATH_IMPORT and type(value) is str:
                params[name] = import_string(value)
        return params

    def render(self, context=None, queryset=None):
        """
        Render the template with the provided context. The context is passed to the Jinja2 environment as a dictionary.
        """
        context = self.get_context(context=context, queryset=queryset)
        env_params = self.get_environment_params()
        output = render_jinja2(self.template_code, context, env_params, getattr(self, 'data_file', None))

        # Replace CRLF-style line terminators
        output = output.replace('\r\n', '\n')

        return output

    def render_to_response(self, context=None, queryset=None):
        output = self.render(context=context, queryset=queryset)
        mime_type = self.mime_type or DEFAULT_MIME_TYPE

        # Build the response
        response = HttpResponse(output, content_type=mime_type)

        if self.as_attachment:
            extension = f'.{self.file_extension}' if self.file_extension else ''
            if self.file_name:
                filename = self.file_name
            elif queryset:
                filename = filename_from_model(queryset.model)
            elif context:
                filename = filename_from_object(context)
            else:
                filename = "output"
            response['Content-Disposition'] = f'attachment; filename="{filename}{extension}"'

        return response
