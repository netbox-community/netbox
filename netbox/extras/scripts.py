import inspect
import json
import logging
import os
import pkgutil
import sys
import threading
import traceback
from datetime import timedelta

import yaml
from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import transaction
from django.utils.functional import classproperty

from extras.api.serializers import ScriptOutputSerializer
from extras.choices import JobResultStatusChoices, LogLevelChoices
from extras.models import JobResult
from extras.signals import clear_webhooks
from ipam.formfields import IPAddressFormField, IPNetworkFormField
from ipam.validators import MaxPrefixLengthValidator, MinPrefixLengthValidator, prefix_validator
from utilities.exceptions import AbortScript, AbortTransaction
from utilities.forms import add_blank_choice, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from .context_managers import change_logging
from .forms import ScriptForm

__all__ = [
    'BaseScript',
    'BooleanVar',
    'ChoiceVar',
    'FileVar',
    'IntegerVar',
    'IPAddressVar',
    'IPAddressWithMaskVar',
    'IPNetworkVar',
    'MultiChoiceVar',
    'MultiObjectVar',
    'ObjectVar',
    'Script',
    'StringVar',
    'TextVar',
]

lock = threading.Lock()


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

        # Set field choices, adding a blank choice to avoid forced selections
        self.field_attrs['choices'] = add_blank_choice(choices)


class MultiChoiceVar(ScriptVariable):
    """
    Like ChoiceVar, but allows for the selection of multiple choices.
    """
    form_field = forms.MultipleChoiceField

    def __init__(self, choices, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set field choices
        self.field_attrs['choices'] = choices


class ObjectVar(ScriptVariable):
    """
    A single object within NetBox.

    :param model: The NetBox model being referenced
    :param query_params: A dictionary of additional query parameters to attach when making REST API requests (optional)
    :param null_option: The label to use as a "null" selection option (optional)
    """
    form_field = DynamicModelChoiceField

    def __init__(self, model, query_params=None, null_option=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.field_attrs.update({
            'queryset': model.objects.all(),
            'query_params': query_params,
            'null_option': null_option,
        })


class MultiObjectVar(ObjectVar):
    """
    Like ObjectVar, but can represent one or more objects.
    """
    form_field = DynamicModelMultipleChoiceField


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

    # Prevent django from instantiating the class on all accesses
    do_not_call_in_templates = True

    class Meta:
        pass

    def __init__(self):

        # Initiate the log
        self.logger = logging.getLogger(f"netbox.scripts.{self.module()}.{self.__class__.__name__}")
        self.log = []

        # Declare the placeholder for the current request
        self.request = None

        # Grab some info about the script
        self.filename = inspect.getfile(self.__class__)
        self.source = inspect.getsource(self.__class__)

    def __str__(self):
        return self.name

    @classproperty
    def name(self):
        return getattr(self.Meta, 'name', self.__name__)

    @classproperty
    def full_name(self):
        return '.'.join([self.__module__, self.__name__])

    @classproperty
    def description(self):
        return getattr(self.Meta, 'description', '')

    @classmethod
    def module(cls):
        return cls.__module__

    @classmethod
    def root_module(cls):
        return cls.__module__.split(".")[0]

    @classproperty
    def job_timeout(self):
        return getattr(self.Meta, 'job_timeout', None)

    @classmethod
    def _get_vars(cls):
        vars = {}

        # Iterate all base classes looking for ScriptVariables
        for base_class in inspect.getmro(cls):
            # When object is reached there's no reason to continue
            if base_class is object:
                break

            for name, attr in base_class.__dict__.items():
                if name not in vars and issubclass(attr.__class__, ScriptVariable):
                    vars[name] = attr

        # Order variables according to field_order
        field_order = getattr(cls.Meta, 'field_order', None)
        if not field_order:
            return vars
        ordered_vars = {
            field: vars.pop(field) for field in field_order if field in vars
        }
        ordered_vars.update(vars)

        return ordered_vars

    def run(self, data, commit):
        raise NotImplementedError("The script must define a run() method.")

    def as_form(self, data=None, files=None, initial=None):
        """
        Return a Django form suitable for populating the context data required to run this Script.
        """
        # Create a dynamic ScriptForm subclass from script variables
        fields = {
            name: var.as_field() for name, var in self._get_vars().items()
        }
        FormClass = type('ScriptForm', (ScriptForm,), fields)

        form = FormClass(data, files, initial=initial)

        # Set initial "commit" checkbox state based on the script's Meta parameter
        form.fields['_commit'].initial = getattr(self.Meta, 'commit_default', True)

        # Append the default fieldset if defined in the Meta class
        default_fieldset = (
            ('Script Execution Parameters', ('_schedule_at', '_interval', '_commit')),
        )
        if not hasattr(self.Meta, 'fieldsets'):
            fields = (
                name for name, _ in self._get_vars().items()
            )
            self.Meta.fieldsets = (('Script Data', fields),)

        self.Meta.fieldsets += default_fieldset

        return form

    # Logging

    def log_debug(self, message):
        self.logger.log(logging.DEBUG, message)
        self.log.append((LogLevelChoices.LOG_DEFAULT, message))

    def log_success(self, message):
        self.logger.log(logging.INFO, message)  # No syslog equivalent for SUCCESS
        self.log.append((LogLevelChoices.LOG_SUCCESS, message))

    def log_info(self, message):
        self.logger.log(logging.INFO, message)
        self.log.append((LogLevelChoices.LOG_INFO, message))

    def log_warning(self, message):
        self.logger.log(logging.WARNING, message)
        self.log.append((LogLevelChoices.LOG_WARNING, message))

    def log_failure(self, message):
        self.logger.log(logging.ERROR, message)
        self.log.append((LogLevelChoices.LOG_FAILURE, message))

    # Convenience functions

    def load_yaml(self, filename):
        """
        Return data from a YAML file
        """
        try:
            from yaml import CLoader as Loader
        except ImportError:
            from yaml import Loader

        file_path = os.path.join(settings.SCRIPTS_ROOT, filename)
        with open(file_path, 'r') as datafile:
            data = yaml.load(datafile, Loader=Loader)

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


def run_script(data, request, commit=True, *args, **kwargs):
    """
    A wrapper for calling Script.run(). This performs error handling and provides a hook for committing changes. It
    exists outside the Script class to ensure it cannot be overridden by a script author.
    """
    job_result = kwargs.pop('job_result')
    job_result.start()

    module, script_name = job_result.name.split('.', 1)
    script = get_script(module, script_name)()

    logger = logging.getLogger(f"netbox.scripts.{module}.{script_name}")
    logger.info(f"Running script (commit={commit})")

    # Add files to form data
    files = request.FILES
    for field_name, fileobj in files.items():
        data[field_name] = fileobj

    # Add the current request as a property of the script
    script.request = request

    def _run_script():
        """
        Core script execution task. We capture this within a subfunction to allow for conditionally wrapping it with
        the change_logging context manager (which is bypassed if commit == False).
        """
        try:
            with transaction.atomic():
                script.output = script.run(data=data, commit=commit)
                job_result.set_status(JobResultStatusChoices.STATUS_COMPLETED)

                if not commit:
                    raise AbortTransaction()

        except AbortTransaction:
            script.log_info("Database changes have been reverted automatically.")
            clear_webhooks.send(request)
        except AbortScript as e:
            script.log_failure(
                f"Script aborted with error: {e}"
            )
            script.log_info("Database changes have been reverted due to error.")
            logger.error(f"Script aborted with error: {e}")
            job_result.set_status(JobResultStatusChoices.STATUS_ERRORED)
            clear_webhooks.send(request)
        except Exception as e:
            stacktrace = traceback.format_exc()
            script.log_failure(
                f"An exception occurred: `{type(e).__name__}: {e}`\n```\n{stacktrace}\n```"
            )
            script.log_info("Database changes have been reverted due to error.")
            logger.error(f"Exception raised during script execution: {e}")
            job_result.set_status(JobResultStatusChoices.STATUS_ERRORED)
            clear_webhooks.send(request)
        finally:
            job_result.data = ScriptOutputSerializer(script).data
            job_result.save()

        logger.info(f"Script completed in {job_result.duration}")

    # Execute the script. If commit is True, wrap it with the change_logging context manager to ensure we process
    # change logging, webhooks, etc.
    if commit:
        with change_logging(request):
            _run_script()
    else:
        _run_script()

    # Schedule the next job if an interval has been set
    if job_result.interval:
        new_scheduled_time = job_result.scheduled + timedelta(minutes=job_result.interval)
        JobResult.enqueue_job(
            run_script,
            name=job_result.name,
            obj_type=job_result.obj_type,
            user=job_result.user,
            schedule_at=new_scheduled_time,
            interval=job_result.interval,
            job_timeout=script.job_timeout,
            data=data,
            request=request,
            commit=commit
        )


def get_scripts(use_names=False):
    """
    Return a dict of dicts mapping all scripts to their modules. Set use_names to True to use each module's human-
    defined name in place of the actual module name.
    """
    scripts = {}

    # Get all modules within the scripts path. These are the user-created files in which scripts are
    # defined.
    modules = list(pkgutil.iter_modules([settings.SCRIPTS_ROOT]))
    modules_bases = set([name.split(".")[0] for _, name, _ in modules])

    # Deleting from sys.modules needs to done behind a lock to prevent race conditions where a module is
    # removed from sys.modules while another thread is importing
    with lock:
        for module_name in list(sys.modules.keys()):
            # Everything sharing a base module path with a module in the script folder is removed.
            # We also remove all modules with a base module called "scripts". This allows modifying imported
            # non-script modules without having to reload the RQ worker.
            module_base = module_name.split(".")[0]
            if module_base == "scripts" or module_base in modules_bases:
                del sys.modules[module_name]

    for importer, module_name, _ in modules:
        module = importer.find_module(module_name).load_module(module_name)

        if use_names and hasattr(module, 'name'):
            module_name = module.name

        module_scripts = {}
        script_order = getattr(module, "script_order", ())
        ordered_scripts = [cls for cls in script_order if is_script(cls)]
        unordered_scripts = [cls for _, cls in inspect.getmembers(module, is_script) if cls not in script_order]

        for cls in [*ordered_scripts, *unordered_scripts]:
            # For scripts in submodules use the full import path w/o the root module as the name
            script_name = cls.full_name.split(".", maxsplit=1)[1]
            module_scripts[script_name] = cls

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
