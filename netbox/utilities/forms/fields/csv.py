from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Q

from utilities.choices import unpack_grouped_choices
from utilities.utils import content_type_identifier

__all__ = (
    'CSVChoiceField',
    'CSVContentTypeField',
    'CSVModelChoiceField',
    'CSVModelMultipleChoiceField',
    'CSVMultipleChoiceField',
    'CSVMultipleContentTypeField',
    'CSVTypedChoiceField',
)


class CSVChoicesMixin:
    STATIC_CHOICES = True

    def __init__(self, *, choices=(), **kwargs):
        super().__init__(choices=choices, **kwargs)
        self.choices = unpack_grouped_choices(choices)


class CSVChoiceField(CSVChoicesMixin, forms.ChoiceField):
    """
    A CSV field which accepts a single selection value.
    """
    pass


class CSVMultipleChoiceField(CSVChoicesMixin, forms.MultipleChoiceField):
    """
    A CSV field which accepts multiple selection values.
    """
    def to_python(self, value):
        if not value:
            return []
        if not isinstance(value, str):
            raise forms.ValidationError(f"Invalid value for a multiple choice field: {value}")
        return value.split(',')


class CSVTypedChoiceField(forms.TypedChoiceField):
    STATIC_CHOICES = True


class CSVModelChoiceField(forms.ModelChoiceField):
    """
    Extends Django's `ModelChoiceField` to provide additional validation for CSV values.
    """
    default_error_messages = {
        'invalid_choice': 'Object not found: %(value)s',
    }

    def to_python(self, value):
        try:
            return super().to_python(value)
        except MultipleObjectsReturned:
            raise forms.ValidationError(
                f'"{value}" is not a unique value for this field; multiple objects were found'
            )


class CSVModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    Extends Django's `ModelMultipleChoiceField` to support comma-separated values.
    """
    default_error_messages = {
        'invalid_choice': 'Object not found: %(value)s',
    }

    def clean(self, value):
        value = value.split(',') if value else []
        return super().clean(value)


class CSVContentTypeField(CSVModelChoiceField):
    """
    CSV field for referencing a single content type, in the form `<app>.<model>`.
    """
    STATIC_CHOICES = True

    def prepare_value(self, value):
        return content_type_identifier(value)

    def to_python(self, value):
        if not value:
            return None
        try:
            app_label, model = value.split('.')
        except ValueError:
            raise forms.ValidationError(f'Object type must be specified as "<app>.<model>"')
        try:
            return self.queryset.get(app_label=app_label, model=model)
        except ObjectDoesNotExist:
            raise forms.ValidationError(f'Invalid object type')


class CSVMultipleContentTypeField(forms.ModelMultipleChoiceField):
    """
    CSV field for referencing one or more content types, in the form `<app>.<model>`.
    """
    STATIC_CHOICES = True

    # TODO: Improve validation of selected ContentTypes
    def prepare_value(self, value):
        if type(value) is str:
            ct_filter = Q()
            for name in value.split(','):
                app_label, model = name.split('.')
                ct_filter |= Q(app_label=app_label, model=model)
            return list(ContentType.objects.filter(ct_filter).values_list('pk', flat=True))
        return content_type_identifier(value)
