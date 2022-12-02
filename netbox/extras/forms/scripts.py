from django import forms
from django.utils.translation import gettext as _

from utilities.forms import BootstrapMixin, DateTimePicker

__all__ = (
    'ScriptForm',
)


class ScriptForm(BootstrapMixin, forms.Form):
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
        label=_("Recurs every"),
        help_text=_("Interval at which this script is re-run (in minutes)")
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Move _commit and _schedule_at to the end of the form
        schedule_at = self.fields.pop('_schedule_at')
        interval = self.fields.pop('_interval')
        commit = self.fields.pop('_commit')
        self.fields['_schedule_at'] = schedule_at
        self.fields['_interval'] = interval
        self.fields['_commit'] = commit

    @property
    def requires_input(self):
        """
        A boolean indicating whether the form requires user input (ignore the built-in fields).
        """
        return bool(len(self.fields) > 3)
