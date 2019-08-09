from collections import OrderedDict
import inspect
import pkgutil

from django import forms
from django.conf import settings

from .constants import LOG_DEFAULT, LOG_FAILURE, LOG_INFO, LOG_SUCCESS, LOG_WARNING
from .forms import ScriptForm


#
# Script variables
#

class ScriptVariable:
    form_field = forms.CharField

    def __init__(self, label='', description=''):

        # Default field attributes
        if not hasattr(self, 'field_attrs'):
            self.field_attrs = {}
        if label:
            self.field_attrs['label'] = label
        if description:
            self.field_attrs['help_text'] = description

    def as_field(self):
        """
        Render the variable as a Django form field.
        """
        return self.form_field(**self.field_attrs)


class StringVar(ScriptVariable):
    pass


class IntegerVar(ScriptVariable):
    form_field = forms.IntegerField


class BooleanVar(ScriptVariable):
    form_field = forms.BooleanField
    field_attrs = {
        'required': False
    }


class ObjectVar(ScriptVariable):
    form_field = forms.ModelChoiceField

    def __init__(self, queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.field_attrs['queryset'] = queryset


class Script:
    """
    Custom scripts inherit this object.
    """

    def __init__(self):

        # Initiate the log
        self.log = []

        # Grab some info about the script
        self.filename = inspect.getfile(self.__class__)
        self.source = inspect.getsource(self.__class__)

    def __str__(self):
        if hasattr(self, 'name'):
            return self.name
        return self.__class__.__name__

    def _get_vars(self):
        # TODO: This should preserve var ordering
        return inspect.getmembers(self, is_variable)

    def run(self, context):
        raise NotImplementedError("The script must define a run() method.")

    def as_form(self, data=None):
        """
        Return a Django form suitable for populating the context data required to run this Script.
        """
        vars = self._get_vars()
        form = ScriptForm(vars, data)

        return form

    # Logging

    def log_debug(self, message):
        self.log.append((LOG_DEFAULT, message))

    def log_success(self, message):
        self.log.append((LOG_SUCCESS, message))

    def log_info(self, message):
        self.log.append((LOG_INFO, message))

    def log_warning(self, message):
        self.log.append((LOG_WARNING, message))

    def log_failure(self, message):
        self.log.append((LOG_FAILURE, message))


#
# Functions
#

def is_script(obj):
    """
    Returns True if the object is a Script.
    """
    return obj in Script.__subclasses__()


def is_variable(obj):
    """
    Returns True if the object is a ScriptVariable.
    """
    return isinstance(obj, ScriptVariable)


def get_scripts():
    scripts = OrderedDict()

    # Iterate through all modules within the reports path. These are the user-created files in which reports are
    # defined.
    for importer, module_name, _ in pkgutil.iter_modules([settings.SCRIPTS_ROOT]):
        module = importer.find_module(module_name).load_module(module_name)
        module_scripts = OrderedDict()
        for name, cls in inspect.getmembers(module, is_script):
            module_scripts[name] = cls
        scripts[module_name] = module_scripts

    return scripts
