from django import forms
from django.utils import timezone
from django.utils.translation import gettext as _

from utilities.forms import BootstrapMixin, DateTimePicker

__all__ = (
    'ReportForm',
)


class ReportForm(BootstrapMixin, forms.Form):
    schedule_at = forms.DateTimeField(
        required=False,
        widget=DateTimePicker(),
        label=_("Schedule at"),
        help_text=_("Schedule execution of report to a set time"),
    )
    interval = forms.IntegerField(
        required=False,
        min_value=1,
        label=_("Recurs every"),
        help_text=_("Interval at which this report is re-run (in minutes)")
    )

    def clean_schedule_at(self):
        scheduled_time = self.cleaned_data['schedule_at']
        if scheduled_time and scheduled_time < timezone.now():
            raise forms.ValidationError(_('Scheduled time must be in the future.'))

        return scheduled_time
