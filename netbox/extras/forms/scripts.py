from core.choices import JobIntervalChoices
from core.forms import ManagedFileForm
from django import forms
from django.core.files.storage import storages
from django.utils.translation import gettext_lazy as _
from utilities.datetime import local_now
from utilities.forms.widgets import DateTimePicker, NumberWithOptions

__all__ = (
    'ScriptFileForm',
    'ScriptForm',
)


class ScriptForm(forms.Form):
    _commit = forms.BooleanField(
        required=False,
        initial=True,
        label=_("Commit changes"),
        help_text=_("Commit changes to the database (uncheck for a dry-run)")
    )
    _schedule_at = forms.DateTimeField(
        required=False,
        widget=DateTimePicker(),
        label=_("Schedule at"),
        help_text=_("Schedule execution of script to a set time"),
    )
    _interval = forms.IntegerField(
        required=False,
        min_value=1,
        label=_("Recurs every"),
        widget=NumberWithOptions(
            options=JobIntervalChoices
        ),
        help_text=_("Interval at which this script is re-run (in minutes)")
    )

    def __init__(self, *args, scheduling_enabled=True, **kwargs):
        super().__init__(*args, **kwargs)

        # Annotate the current system time for reference
        now = local_now().strftime('%Y-%m-%d %H:%M:%S %Z')
        self.fields['_schedule_at'].help_text += _(' (current time: <strong>{now}</strong>)').format(now=now)

        # Remove scheduling fields if scheduling is disabled
        if not scheduling_enabled:
            self.fields.pop('_schedule_at')
            self.fields.pop('_interval')

    def clean(self):
        scheduled_time = self.cleaned_data.get('_schedule_at')
        if scheduled_time and scheduled_time < local_now():
            raise forms.ValidationError(_('Scheduled time must be in the future.'))

        # When interval is used without schedule at, schedule for the current time
        if self.cleaned_data.get('_interval') and not scheduled_time:
            self.cleaned_data['_schedule_at'] = local_now()

        return self.cleaned_data


class ScriptFileForm(ManagedFileForm):
    """
    ManagedFileForm with a custom save method to use django-storages.
    """
    def save(self, *args, **kwargs):
        # If a file was uploaded, save it to disk
        if self.cleaned_data['upload_file']:
            storage = storages.create_storage(storages.backends["scripts"])

            filename = self.cleaned_data['upload_file'].name
            self.instance.file_path = filename
            data = self.cleaned_data['upload_file']
            storage.save(filename, data)

        # need to skip ManagedFileForm save method
        return super(ManagedFileForm, self).save(*args, **kwargs)
