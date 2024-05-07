import time

from django import forms
from django.utils.translation import gettext_lazy as _

__all__ = (
    'CheckLastUpdatedMixin',
)


class CheckLastUpdatedMixin(forms.Form):
    """
    Checks whether the object being saved has been updated since the form was initialized. If so, validation fails.
    This prevents a user from inadvertently overwriting any changes made to the object between when the form was
    initialized and when it was submitted.

    This validation does not apply to newly created objects, or if the `_init_time` field is not present in the form
    data.
    """
    _init_time = forms.DecimalField(
        initial=time.time,
        required=False,
        widget=forms.HiddenInput()
    )

    def clean(self):
        super().clean()

        # Skip for absent or newly created instances
        if not self.instance or not self.instance.pk:
            return

        # Skip if a form init time has not been specified
        if not (form_init_time := self.cleaned_data.get('_init_time')):
            return

        # Skip if the object does not have a last_updated value
        if not (last_updated := getattr(self.instance, 'last_updated', None)):
            return

        # Check that the submitted initialization time is not earlier than the object's modification time
        if form_init_time < last_updated.timestamp():
            raise forms.ValidationError(_(
                "This object has been modified since the form was rendered. Please consult the object's change "
                "log for details."
            ))
