from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _

from dcim.constants import LOCATION_SCOPE_TYPES
from dcim.models import Site
from utilities.forms import get_field_value
from utilities.forms.fields import (
    ContentTypeChoiceField, CSVContentTypeField, DynamicModelChoiceField,
)
from utilities.templatetags.builtins.filters import bettertitle
from utilities.forms.widgets import HTMXSelect

__all__ = (
    'ScopedBulkEditForm',
    'ScopedForm',
    'ScopedImportForm',
)


class ScopedForm(forms.Form):
    scope_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(model__in=LOCATION_SCOPE_TYPES),
        widget=HTMXSelect(),
        required=False,
        label=_('Scope type')
    )
    scope = DynamicModelChoiceField(
        label=_('Scope'),
        queryset=Site.objects.none(),  # Initial queryset
        required=False,
        disabled=True,
        selector=True
    )

    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance')
        initial = kwargs.get('initial', {})

        if instance is not None and instance.scope:
            initial['scope'] = instance.scope
            kwargs['initial'] = initial

        super().__init__(*args, **kwargs)
        self._set_scoped_values()

    def clean(self):
        super().clean()

        # Assign the selected scope (if any)
        self.instance.scope = self.cleaned_data.get('scope')

    def _set_scoped_values(self):
        if scope_type_id := get_field_value(self, 'scope_type'):
            try:
                scope_type = ContentType.objects.get(pk=scope_type_id)
                model = scope_type.model_class()
                self.fields['scope'].queryset = model.objects.all()
                self.fields['scope'].widget.attrs['selector'] = model._meta.label_lower
                self.fields['scope'].disabled = False
                self.fields['scope'].label = _(bettertitle(model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass

            if self.instance and scope_type_id != self.instance.scope_type_id:
                self.initial['scope'] = None


class ScopedBulkEditForm(forms.Form):
    scope_type = ContentTypeChoiceField(
        queryset=ContentType.objects.filter(model__in=LOCATION_SCOPE_TYPES),
        widget=HTMXSelect(method='post', attrs={'hx-select': '#form_fields'}),
        required=False,
        label=_('Scope type')
    )
    scope = DynamicModelChoiceField(
        label=_('Scope'),
        queryset=Site.objects.none(),  # Initial queryset
        required=False,
        disabled=True,
        selector=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if scope_type_id := get_field_value(self, 'scope_type'):
            try:
                scope_type = ContentType.objects.get(pk=scope_type_id)
                model = scope_type.model_class()
                self.fields['scope'].queryset = model.objects.all()
                self.fields['scope'].widget.attrs['selector'] = model._meta.label_lower
                self.fields['scope'].disabled = False
                self.fields['scope'].label = _(bettertitle(model._meta.verbose_name))
            except ObjectDoesNotExist:
                pass


class ScopedImportForm(forms.Form):
    scope_type = CSVContentTypeField(
        queryset=ContentType.objects.filter(model__in=LOCATION_SCOPE_TYPES),
        required=False,
        label=_('Scope type (app & model)')
    )
