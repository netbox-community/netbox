from django import forms

from utilities.forms import BootstrapMixin, DateTimePicker

__all__ = (
    'ReportForm',
)


class ReportForm(BootstrapMixin, forms.Form):
    schedule_at = forms.DateTimeField(
        required=False,
        widget=DateTimePicker(),
        label="Schedule at",
        help_text="Schedule execution of report to a set time",
    )