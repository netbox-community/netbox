import csv
from io import StringIO

from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import gettext as _

from utilities.choices import unpack_grouped_choices
from utilities.forms.utils import parse_csv, validate_csv
from utilities.utils import content_type_identifier

__all__ = (
    'CSVChoiceField',
    'CSVContentTypeField',
    'CSVDataField',
    'CSVFileField',
    'CSVModelChoiceField',
    'CSVModelMultipleChoiceField',
    'CSVMultipleChoiceField',
    'CSVMultipleContentTypeField',
    'CSVTypedChoiceField',
)


class CSVDataField(forms.CharField):
    """
    A CharField (rendered as a Textarea) which accepts CSV-formatted data. It returns data as a two-tuple: The first
    item is a dictionary of column headers, mapping field names to the attribute by which they match a related object
    (where applicable). The second item is a list of dictionaries, each representing a discrete row of CSV data.

    :param from_form: The form from which the field derives its validation rules.
    """
    widget = forms.Textarea

    def __init__(self, from_form, *args, **kwargs):

        form = from_form()
        self.model = form.Meta.model
        self.fields = form.fields
        self.required_fields = [
            name for name, field in form.fields.items() if field.required
        ]

        super().__init__(*args, **kwargs)

        self.strip = False
        if not self.label:
            self.label = ''
        if not self.initial:
            self.initial = ','.join(self.required_fields) + '\n'
        if not self.help_text:
            self.help_text = _('Enter the list of column headers followed by one line per record to be imported, using '
                               'commas to separate values. Multi-line data and values containing commas may be wrapped '
                               'in double quotes.')

    def to_python(self, value):
        reader = csv.reader(StringIO(value.strip()))

        return parse_csv(reader)

    def validate(self, value):
        headers, records = value
        validate_csv(headers, self.fields, self.required_fields)

        return value


class CSVFileField(forms.FileField):
    """
    A FileField (rendered as a file input button) which accepts a file containing CSV-formatted data. It returns
    data as a two-tuple: The first item is a dictionary of column headers, mapping field names to the attribute
    by which they match a related object (where applicable). The second item is a list of dictionaries, each
    representing a discrete row of CSV data.

    :param from_form: The form from which the field derives its validation rules.
    """

    def __init__(self, from_form, *args, **kwargs):

        form = from_form()
        self.model = form.Meta.model
        self.fields = form.fields
        self.required_fields = [
            name for name, field in form.fields.items() if field.required
        ]

        super().__init__(*args, **kwargs)

    def to_python(self, file):
        if file is None:
            return None

        csv_str = file.read().decode('utf-8').strip()
        reader = csv.reader(StringIO(csv_str))
        headers, records = parse_csv(reader)

        return headers, records

    def validate(self, value):
        if value is None:
            return None

        headers, records = value
        validate_csv(headers, self.fields, self.required_fields)

        return value


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
