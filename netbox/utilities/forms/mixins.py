import time

from django import forms
from django.utils.translation import gettext_lazy as _

from utilities.conversion import to_meters

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


class DistanceValidationMixin(forms.Form):
    def clean(self):
        super().clean()

        # validate max distance in meters based on model
        # breakpoint()
        distance = self.cleaned_data.get('distance', None)
        unit = self.cleaned_data.get('distance_unit', None)
        if distance and unit:
            model_class = self._meta.model
            distance_field = model_class._meta.get_field('distance')
            max_digits = distance_field.max_digits - distance_field.decimal_places
            max_distance = 10 ** max_digits

            abs_distance = to_meters(distance, unit)

            if abs_distance > max_distance:
                raise forms.ValidationError(_(
                    "{distance} {unit} ({abs_distance} m) exceeds the maximum allowed distance for "
                    "{model._meta.verbose_name} distance. Distance must normalize to no more than "
                    "{max_distance} meters.".format(
                        distance=distance,
                        unit=unit,
                        abs_distance=abs_distance,
                        model=model_class,
                        max_distance=max_distance
                    )
                ))

            self.cleaned_data['_abs_distance'] = abs_distance
