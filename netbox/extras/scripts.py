import inspect
import json
import os
import pkgutil
import time
import traceback
from collections import OrderedDict

import yaml
from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import transaction
from mptt.forms import TreeNodeChoiceField, TreeNodeMultipleChoiceField
from mptt.models import MPTTModel

from ipam.formfields import IPAddressFormField, IPNetworkFormField
from ipam.validators import MaxPrefixLengthValidator, MinPrefixLengthValidator, prefix_validator
from .constants import LOG_DEFAULT, LOG_FAILURE, LOG_INFO, LOG_SUCCESS, LOG_WARNING
from utilities.exceptions import AbortTransaction
from utilities.forms import DynamicModelChoiceField, DynamicModelMultipleChoiceField
from .forms import ScriptForm
from .signals import purge_changelog

__all__ = [
    'BaseScript',
    'BooleanVar',
    'ChoiceVar',
    'FileVar',
    'IntegerVar',
    'IPAddressVar',
    'IPAddressWithMaskVar',
    'IPNetworkVar',
    'MultiObjectVar',
    'ObjectVar',
    'Script',
    'StringVar',
    'TextVar',
]


#
# Script variables
#

class ScriptVariable:
    """
    Base model for script variables
    """
    form_field = forms.CharField

    def __init__(self, label='', description='', default=None, required=True, widget=None):

        # Initialize field attributes
        if not hasattr(self, 'field_attrs'):
            self.field_attrs = {}
        if label:
            self.field_attrs['label'] = label
        if description:
            self.field_attrs['help_text'] = description
        if default:
            self.field_attrs['initial'] = default
        if widget:
            self.field_attrs['widget'] = widget
        self.field_attrs['required'] = required

    def as_field(self):
        """
        Render the variable as a Django form field.
        """
        form_field = self.form_field(**self.field_attrs)
        if not isinstance(form_field.widget, forms.CheckboxInput):
            if form_field.widget.attrs and 'class' in form_field.widget.attrs.keys():
                form_field.widget.attrs['class'] += ' form-control'
            else:
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


class TextVar(ScriptVariable):
    """
    Free-form text data. Renders as a <textarea>.
    """
    form_field = forms.CharField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.field_attrs['widget'] = forms.Textarea


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


class ChoiceVar(ScriptVariable):
    """
    Select one of several predefined static choices, passed as a list of two-tuples. Example:

        color = ChoiceVar(
            choices=(
                ('#ff0000', 'Red'),
                ('#00ff00', 'Green'),
                ('#0000ff', 'Blue')
            )
        )
    """
    form_field = forms.ChoiceField

    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set field choices
        self.field_attrs['choices'] = choices


class ObjectVar(ScriptVariable):
    """
    NetBox object representation. The provided QuerySet will determine the choices available.
    """
    form_field = DynamicModelChoiceField

    def __init__(self, queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Queryset for field choices
        self.field_attrs['queryset'] = queryset

        # Update form field for MPTT (nested) objects
        if issubclass(queryset.model, MPTTModel):
            self.form_field = TreeNodeChoiceField


class MultiObjectVar(ScriptVariable):
    """
    Like ObjectVar, but can represent one or more objects.
    """
    form_field = DynamicModelMultipleChoiceField

    def __init__(self, queryset, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Queryset for field choices
        self.field_attrs['queryset'] = queryset

        # Update form field for MPTT (nested) objects
        if issubclass(queryset.model, MPTTModel):
            self.form_field = TreeNodeMultipleChoiceField


class FileVar(ScriptVariable):
    """
    An uploaded file.
    """
    form_field = forms.FileField


class IPAddressVar(ScriptVariable):
    """
    An IPv4 or IPv6 address without a mask.
    """
    form_field = IPAddressFormField


class IPAddressWithMaskVar(ScriptVariable):
    """
    An IPv4 or IPv6 address with a mask.
    """
    form_field = IPNetworkFormField


class IPNetworkVar(ScriptVariable):
    """
    An IPv4 or IPv6 prefix.
    """
    form_field = IPNetworkFormField

    def __init__(self, min_prefix_length=None, max_prefix_length=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set prefix validator and optional minimum/maximum prefix lengths
        self.field_attrs['validators'] = [prefix_validator]
        if min_prefix_length is not None:
            self.field_attrs['validators'].append(
                MinPrefixLengthValidator(min_prefix_length)
            )
        if max_prefix_length is not None:
            self.field_attrs['validators'].append(
                MaxPrefixLengthValidator(max_prefix_length)
            )


#
# Scripts
#

class BaseScript:
    """
    Base model for custom scripts. User classes should inherit from this model if they want to extend Script
    functionality for use in other subclasses.
    """
    class Meta:
        pass

    def __init__(self):

        # Initiate the log
        self.log = []

        # Declare the placeholder for the current request
        self.request = None

        # Grab some info about the script
        self.filename = inspect.getfile(self.__class__)
        self.source = inspect.getsource(self.__class__)

    def __str__(self):
        return getattr(self.Meta, 'name', self.__class__.__name__)

    @classmethod
    def module(cls):
        return cls.__module__

    @classmethod
    def _get_vars(cls):
        vars = OrderedDict()

        # Infer order from Meta.field_order (Python 3.5 and lower)
        field_order = getattr(cls.Meta, 'field_order', [])
        for name in field_order:
            vars[name] = getattr(cls, name)

        # Default to order of declaration on class
        for name, attr in cls.__dict__.items():
            if name not in vars and issubclass(attr.__class__, ScriptVariable):
                vars[name] = attr

        return vars

    def run(self, data, commit):
        raise NotImplementedError("The script must define a run() method.")

    def as_form(self, data=None, files=None, initial=None):
        """
        Return a Django form suitable for populating the context data required to run this Script.
        """
        vars = self._get_vars()
        form = ScriptForm(vars, data, files, initial=initial, commit_default=getattr(self.Meta, 'commit_default', True))

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

    # Convenience functions

    def load_yaml(self, filename):
        """
        Return data from a YAML file
        """
        file_path = os.path.join(settings.SCRIPTS_ROOT, filename)
        with open(file_path, 'r') as datafile:
            data = yaml.load(datafile)

        return data

    def load_json(self, filename):
        """
        Return data from a JSON file
        """
        file_path = os.path.join(settings.SCRIPTS_ROOT, filename)
        with open(file_path, 'r') as datafile:
            data = json.load(datafile)

        return data


class Script(BaseScript):
    """
    Classes which inherit this model will appear in the list of available scripts.
    """
    pass


#
# Functions
#

def is_script(obj):
    """
    Returns True if the object is a Script.
    """
    try:
        return issubclass(obj, Script) and obj != Script
    except TypeError:
        return False


def is_variable(obj):
    """
    Returns True if the object is a ScriptVariable.
    """
    return isinstance(obj, ScriptVariable)


def run_script(script, data, request, commit=True):
    """
    A wrapper for calling Script.run(). This performs error handling and provides a hook for committing changes. It
    exists outside of the Script class to ensure it cannot be overridden by a script author.
    """
    output = None
    start_time = None
    end_time = None

    # Add files to form data
    files = request.FILES
    for field_name, fileobj in files.items():
        data[field_name] = fileobj

    # Add the current request as a property of the script
    script.request = request

    # Determine whether the script accepts a 'commit' argument (this was introduced in v2.7.8)
    kwargs = {
        'data': data
    }
    if 'commit' in inspect.signature(script.run).parameters:
        kwargs['commit'] = commit

    try:
        with transaction.atomic():
            start_time = time.time()
            output = script.run(**kwargs)
            end_time = time.time()
            if not commit:
                raise AbortTransaction()
    except AbortTransaction:
        pass
    except Exception as e:
        stacktrace = traceback.format_exc()
        script.log_failure(
            "An exception occurred: `{}: {}`\n```\n{}\n```".format(type(e).__name__, e, stacktrace)
        )
        commit = False
    finally:
        if not commit:
            # Delete all pending changelog entries
            purge_changelog.send(Script)
            script.log_info(
                "Database changes have been reverted automatically."
            )

    # Calculate execution time
    if end_time is not None:
        execution_time = end_time - start_time
    else:
        execution_time = None

    return output, execution_time


def get_scripts(use_names=False):
    """
    Return a dict of dicts mapping all scripts to their modules. Set use_names to True to use each module's human-
    defined name in place of the actual module name.
    """
    scripts = OrderedDict()

    # Iterate through all modules within the reports path. These are the user-created files in which reports are
    # defined.
    for importer, module_name, _ in pkgutil.iter_modules([settings.SCRIPTS_ROOT]):
        module = importer.find_module(module_name).load_module(module_name)
        if use_names and hasattr(module, 'name'):
            module_name = module.name
        module_scripts = OrderedDict()
        for name, cls in inspect.getmembers(module, is_script):
            module_scripts[name] = cls
        if module_scripts:
            scripts[module_name] = module_scripts

    return scripts


def get_script(module_name, script_name):
    """
    Retrieve a script class by module and name. Returns None if the script does not exist.
    """
    scripts = get_scripts()
    module = scripts.get(module_name)
    if module:
        return module.get(script_name)
