import inspect
import json
import logging
import os
import traceback
from datetime import timedelta

import yaml
from django import forms
from django.conf import settings
from django.core.validators import RegexValidator
from django.db import transaction
from django.utils import timezone
from django.utils.functional import classproperty
from django.utils.translation import gettext as _

from core.choices import JobStatusChoices
from core.models import Job
from extras.choices import LogLevelChoices
from extras.models import ScriptModule, Script as ScriptModel
from extras.signals import clear_events
from ipam.formfields import IPAddressFormField, IPNetworkFormField
from ipam.validators import MaxPrefixLengthValidator, MinPrefixLengthValidator, prefix_validator
from netbox.context_managers import event_tracking
from utilities.exceptions import AbortScript, AbortTransaction
from utilities.forms import add_blank_choice
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.widgets import DatePicker, DateTimePicker
from .forms import ScriptForm
from .utils import is_report


__all__ = (
    'BaseScript',
    'BooleanVar',
    'ChoiceVar',
    'DateVar',
    'DateTimeVar',
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
    'get_module_and_script',
    'run_script',
)


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


class DateVar(ScriptVariable):
    """
    A date.
    """
    form_field = forms.DateField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_field.widget = DatePicker()


class DateTimeVar(ScriptVariable):
    """
    A date and a time.
    """
    form_field = forms.DateTimeField

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_field.widget = DateTimePicker()


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
    :param context: A custom dictionary mapping template context variables to fields, used when rendering <option>
        elements within the dropdown menu (optional)
    :param null_option: The label to use as a "null" selection option (optional)
    """
    form_field = DynamicModelChoiceField

    def __init__(self, model, query_params=None, context=None, null_option=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.field_attrs.update({
            'queryset': model.objects.all(),
            'query_params': query_params,
            'context': context,
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
        self.messages = []  # Primary script log
        self.tests = {}  # Mapping of logs for test methods
        self.output = ''
        self.failed = False
        self._current_test = None  # Tracks the current test method being run (if any)

        # Initiate the log
        self.logger = logging.getLogger(f"netbox.scripts.{self.__module__}.{self.__class__.__name__}")

        # Declare the placeholder for the current request
        self.request = None

        # Compile test methods and initialize results skeleton
        for method in dir(self):
            if method.startswith('test_') and callable(getattr(self, method)):
                self.tests[method] = {
                    LogLevelChoices.LOG_SUCCESS: 0,
                    LogLevelChoices.LOG_INFO: 0,
                    LogLevelChoices.LOG_WARNING: 0,
                    LogLevelChoices.LOG_FAILURE: 0,
                    'log': [],
                }

    def __str__(self):
        return self.name

    @classproperty
    def module(self):
        return self.__module__

    @classproperty
    def class_name(self):
        return self.__name__

    @classproperty
    def full_name(self):
        return f'{self.module}.{self.class_name}'

    @classmethod
    def root_module(cls):
        return cls.__module__.split(".")[0]

    # Author-defined attributes

    @classproperty
    def name(self):
        return getattr(self.Meta, 'name', self.__name__)

    @classproperty
    def description(self):
        return getattr(self.Meta, 'description', '')

    @classproperty
    def field_order(self):
        return getattr(self.Meta, 'field_order', None)

    @classproperty
    def fieldsets(self):
        return getattr(self.Meta, 'fieldsets', None)

    @classproperty
    def commit_default(self):
        return getattr(self.Meta, 'commit_default', True)

    @classproperty
    def job_timeout(self):
        return getattr(self.Meta, 'job_timeout', None)

    @classproperty
    def scheduling_enabled(self):
        return getattr(self.Meta, 'scheduling_enabled', True)

    @property
    def filename(self):
        return inspect.getfile(self.__class__)

    @property
    def source(self):
        return inspect.getsource(self.__class__)

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
        if not cls.field_order:
            return vars
        ordered_vars = {
            field: vars.pop(field) for field in cls.field_order if field in vars
        }
        ordered_vars.update(vars)

        return ordered_vars

    def run(self, data, commit):
        """
        Override this method with custom script logic.
        """

        # Backward compatibility for legacy Reports
        self.pre_run()
        self.run_tests()
        self.post_run()

    def get_job_data(self):
        """
        Return a dictionary of data to attach to the script's Job.
        """
        return {
            'log': self.messages,
            'output': self.output,
            'tests': self.tests,
        }

    #
    # Form rendering
    #

    def get_fieldsets(self):
        fieldsets = []

        if self.fieldsets:
            fieldsets.extend(self.fieldsets)
        else:
            fields = list(name for name, _ in self._get_vars().items())
            fieldsets.append((_('Script Data'), fields))

        # Append the default fieldset if defined in the Meta class
        exec_parameters = ('_schedule_at', '_interval', '_commit') if self.scheduling_enabled else ('_commit',)
        fieldsets.append((_('Script Execution Parameters'), exec_parameters))

        return fieldsets

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
        form.fields['_commit'].initial = self.commit_default

        # Hide fields if scheduling has been disabled
        if not self.scheduling_enabled:
            form.fields['_schedule_at'].widget = forms.HiddenInput()
            form.fields['_interval'].widget = forms.HiddenInput()

        return form

    #
    # Logging
    #

    def _log(self, message, obj=None, level=LogLevelChoices.LOG_DEFAULT):
        """
        Log a message. Do not call this method directly; use one of the log_* wrappers below.
        """
        if level not in LogLevelChoices.values():
            raise ValueError(f"Invalid logging level: {level}")

        # A test method is currently active, so log the message using legacy Report logging
        if self._current_test:

            # Increment the event counter for this level
            if level in self.tests[self._current_test]:
                self.tests[self._current_test][level] += 1

            # Record message (if any) to the report log
            if message:
                # TODO: Use a dataclass for test method logs
                self.tests[self._current_test]['log'].append((
                    timezone.now().isoformat(),
                    level,
                    str(obj) if obj else None,
                    obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else None,
                    str(message),
                ))

        elif message:

            # Record to the script's log
            self.messages.append({
                'time': timezone.now().isoformat(),
                'status': level,
                'message': str(message),
                'obj': str(obj) if obj else None,
                'url': obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else None,
            })

            # Record to the system log
            if obj:
                message = f"{obj}: {message}"
            self.logger.log(LogLevelChoices.SYSTEM_LEVELS[level], message)

    def log_debug(self, message=None, obj=None):
        self._log(message, obj, level=LogLevelChoices.LOG_DEBUG)

    def log_success(self, message=None, obj=None):
        self._log(message, obj, level=LogLevelChoices.LOG_SUCCESS)

    def log_info(self, message=None, obj=None):
        self._log(message, obj, level=LogLevelChoices.LOG_INFO)

    def log_warning(self, message=None, obj=None):
        self._log(message, obj, level=LogLevelChoices.LOG_WARNING)

    def log_failure(self, message=None, obj=None):
        self._log(message, obj, level=LogLevelChoices.LOG_FAILURE)
        self.failed = True

    #
    # Convenience functions
    #

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

    #
    # Legacy Report functionality
    #

    def run_tests(self):
        """
        Run the report and save its results. Each test method will be executed in order.
        """
        self.logger.info(f"Running report")

        try:
            for test_name in self.tests:
                self._current_test = test_name
                test_method = getattr(self, test_name)
                test_method()
                self._current_test = None
        except Exception as e:
            self._current_test = None
            self.post_run()
            raise e

    def pre_run(self):
        """
        Legacy method for operations performed immediately prior to running a Report.
        """
        pass

    def post_run(self):
        """
        Legacy method for operations performed immediately after running a Report.
        """
        pass


class Script(BaseScript):
    """
    Classes which inherit this model will appear in the list of available scripts.
    """
    pass


#
# Functions
#


def is_variable(obj):
    """
    Returns True if the object is a ScriptVariable.
    """
    return isinstance(obj, ScriptVariable)


def get_module_and_script(module_name, script_name):
    module = ScriptModule.objects.get(file_path=f'{module_name}.py')
    script = module.scripts.get(name=script_name)
    return module, script


def run_script(data, job, request=None, commit=True, **kwargs):
    """
    A wrapper for calling Script.run(). This performs error handling and provides a hook for committing changes. It
    exists outside the Script class to ensure it cannot be overridden by a script author.

    Args:
        data: A dictionary of data to be passed to the script upon execution
        job: The Job associated with this execution
        request: The WSGI request associated with this execution (if any)
        commit: Passed through to Script.run()
    """
    job.start()

    script = ScriptModel.objects.get(pk=job.object_id).python_class()

    logger = logging.getLogger(f"netbox.scripts.{script.full_name}")
    logger.info(f"Running script (commit={commit})")

    # Add files to form data
    if request:
        files = request.FILES
        for field_name, fileobj in files.items():
            data[field_name] = fileobj

    # Add the current request as a property of the script
    script.request = request

    def set_job_data(script):
        job.data = {
            'log': script.messages,
            'output': script.output,
            'tests': script.tests,
        }

        return job

    def _run_script(job):
        """
        Core script execution task. We capture this within a subfunction to allow for conditionally wrapping it with
        the event_tracking context manager (which is bypassed if commit == False).
        """
        try:
            try:
                with transaction.atomic():
                    script.output = script.run(data, commit)
                    if not commit:
                        raise AbortTransaction()
            except AbortTransaction:
                script.log_info(message=_("Database changes have been reverted automatically."))
                if request:
                    clear_events.send(request)

            job.data = script.get_job_data()
            if script.failed:
                logger.warning(f"Script failed")
                job.terminate(status=JobStatusChoices.STATUS_FAILED)
            else:
                job.terminate()

        except Exception as e:
            if type(e) is AbortScript:
                msg = _("Script aborted with error: ") + str(e)
                if is_report(type(script)):
                    script.log_failure(message=msg)
                else:
                    script.log_failure(msg)

                logger.error(f"Script aborted with error: {e}")
            else:
                stacktrace = traceback.format_exc()
                script.log_failure(
                    message=_("An exception occurred: ") + f"`{type(e).__name__}: {e}`\n```\n{stacktrace}\n```"
                )
                logger.error(f"Exception raised during script execution: {e}")
            script.log_info(message=_("Database changes have been reverted due to error."))

            job.data = script.get_job_data()
            job.terminate(status=JobStatusChoices.STATUS_ERRORED, error=repr(e))
            if request:
                clear_events.send(request)

        logger.info(f"Script completed in {job.duration}")

    # Execute the script. If commit is True, wrap it with the event_tracking context manager to ensure we process
    # change logging, event rules, etc.
    if commit:
        with event_tracking(request):
            _run_script(job)
    else:
        _run_script(job)

    # Schedule the next job if an interval has been set
    if job.interval:
        new_scheduled_time = job.scheduled + timedelta(minutes=job.interval)
        Job.enqueue(
            run_script,
            instance=job.object,
            name=job.name,
            user=job.user,
            schedule_at=new_scheduled_time,
            interval=job.interval,
            job_timeout=script.job_timeout,
            data=data,
            request=request,
            commit=commit
        )
