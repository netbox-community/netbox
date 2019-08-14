from collections import OrderedDict
import inspect
import pkgutil

from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import transaction

from ipam.formfields import IPFormField
from utilities.exceptions import AbortTransaction
from .constants import LOG_DEFAULT, LOG_FAILURE, LOG_INFO, LOG_SUCCESS, LOG_WARNING
from .forms import ScriptForm


__all__ = [
    'Script',
    'StringVar',
    'IntegerVar',
    'BooleanVar',
    'ObjectVar',
    'IPNetworkVar',
]


#
# Script variables
#

class ScriptVariable:
    """
    Base model for script variables
    """
    form_field = forms.CharField

    def __init__(self, label='', description='', default=None, required=True):

        # Default field attributes
        self.field_attrs = {
            'help_text': description,
            'required': required
        }
        if label:
            self.field_attrs['label'] = label
        if default:
            self.field_attrs['initial'] = default

    def as_field(self):
        """
        Render the variable as a Django form field.
        """
        form_field = self.form_field(**self.field_attrs)
        form_field.widget.attrs['class'] = 'form-control'

        return form_field


class StringVar(ScriptVariable):
    """
    Character string representation. Can enforce minimum/maximum length and/or regex validation.
    """
    def __init__(self, min_length=None, max_length=None, regex=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Optional minimum/maximum lengths
        if min_length:
            self.field_attrs['min_length'] = min_length
        if max_length:
            self.field_attrs['max_length'] = max_length

        # Optional regular expression validation
        if regex:
            self.field_attrs['validators'] = [
                RegexValidator(
                    regex=regex,
                    message='Invalid value. Must match regex: {}'.format(regex),
                    code='invalid'
                )
            ]


class IntegerVar(ScriptVariable):
    """
    Integer representation. Can enforce minimum/maximum values.
    """
    form_field = forms.IntegerField

    def __init__(self, min_value=None, max_value=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Optional minimum/maximum values
        if min_value:
            self.field_attrs['min_value'] = min_value
        if max_value:
            self.field_attrs['max_value'] = max_value


class BooleanVar(ScriptVariable):
    """
    Boolean representation (true/false). Renders as a checkbox.
    """
    form_field = forms.BooleanField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Boolean fields cannot be required
        self.field_attrs['required'] = False


class ObjectVar(ScriptVariable):
    """
    NetBox object representation. The provided QuerySet will determine the choices available.
    """
    form_field = forms.ModelChoiceField

    def __init__(self, queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Queryset for field choices
        self.field_attrs['queryset'] = queryset


class IPNetworkVar(ScriptVariable):
    """
    An IPv4 or IPv6 prefix.
    """
    form_field = IPFormField


#
# Scripts
#

class Script:
    """
    Custom scripts inherit this object.
    """
    class Meta:
        pass

    def __init__(self):

        # Initiate the log
        self.log = []

        # Grab some info about the script
        self.filename = inspect.getfile(self.__class__)
        self.source = inspect.getsource(self.__class__)

    def __str__(self):
        return getattr(self.Meta, 'name', self.__class__.__name__)

    def _get_vars(self):
        vars = OrderedDict()

        # Infer order from Meta.fields (Python 3.5 and lower)
        fields = getattr(self.Meta, 'fields', [])
        for name in fields:
            vars[name] = getattr(self, name)

        # Default to order of declaration on class
        for name, attr in self.__class__.__dict__.items():
            if name not in vars and issubclass(attr.__class__, ScriptVariable):
                vars[name] = attr

        return vars

    def run(self, data):
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


def run_script(script, data, commit=True):
    """
    A wrapper for calling Script.run(). This performs error handling and provides a hook for committing changes. It
    exists outside of the Script class to ensure it cannot be overridden by a script author.
    """
    output = None

    try:
        with transaction.atomic():
            output = script.run(data)
            if not commit:
                raise AbortTransaction()
    except AbortTransaction:
        pass
    except Exception as e:
        script.log_failure(
            "An exception occurred. {}: {}".format(type(e).__name__, e)
        )
        commit = False
    finally:
        if not commit:
            script.log_info(
                "Database changes have been reverted automatically."
            )

    return output


def get_scripts():
    scripts = OrderedDict()

    # Iterate through all modules within the reports path. These are the user-created files in which reports are
    # defined.
    for importer, module_name, _ in pkgutil.iter_modules([settings.SCRIPTS_ROOT]):
        module = importer.find_module(module_name).load_module(module_name)
        if hasattr(module, 'name'):
            module_name = module.name
        module_scripts = OrderedDict()
        for name, cls in inspect.getmembers(module, is_script):
            module_scripts[name] = cls
        scripts[module_name] = module_scripts

    return scripts
