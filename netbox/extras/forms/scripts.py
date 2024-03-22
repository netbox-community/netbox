from django import forms
from django.utils.translation import gettext_lazy as _

from extras.choices import DurationChoices
from utilities.forms.widgets import DateTimePicker, NumberWithOptions
from utilities.datetime import local_now

__all__ = (
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
            options=DurationChoices
        ),
        help_text=_("Interval at which this script is re-run (in minutes)")
    )

    def __init__(self, *args, scheduling_enabled=True, **kwargs):
        super().__init__(*args, **kwargs)

        # Annotate the current system time for reference
        now = local_now().strftime('%Y-%m-%d %H:%M:%S')
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
