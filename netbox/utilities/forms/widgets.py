import json
from typing import Dict, Sequence, Union

from django import forms
from django.conf import settings
from django.contrib.postgres.forms import SimpleArrayField

from utilities.choices import ColorChoices
from .utils import add_blank_choice, parse_numeric_range

__all__ = (
    'APISelect',
    'APISelectMultiple',
    'BulkEditNullBooleanSelect',
    'ColorSelect',
    'ContentTypeSelect',
    'DatePicker',
    'DateTimePicker',
    'NumericArrayField',
    'SelectSpeedWidget',
    'SelectWithDisabled',
    'SelectWithPK',
    'SlugWidget',
    'SmallTextarea',
    'StaticSelect',
    'StaticSelectMultiple',
    'TimePicker',
)

JSONPrimitive = Union[str, bool, int, float, None]


class SmallTextarea(forms.Textarea):
    """
    Subclass used for rendering a smaller textarea element.
    """
    pass


class SlugWidget(forms.TextInput):
    """
    Subclass TextInput and add a slug regeneration button next to the form field.
    """
    template_name = 'widgets/sluginput.html'


class ColorSelect(forms.Select):
    """
    Extends the built-in Select widget to colorize each <option>.
    """
    option_template_name = 'widgets/colorselect_option.html'

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = add_blank_choice(ColorChoices)
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'netbox-color-select'


class BulkEditNullBooleanSelect(forms.NullBooleanSelect):
    """
    A Select widget for NullBooleanFields
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Override the built-in choice labels
        self.choices = (
            ('1', '---------'),
            ('2', 'Yes'),
            ('3', 'No'),
        )
        self.attrs['class'] = 'netbox-static-select'


class SelectWithDisabled(forms.Select):
    """
    Modified the stock Select widget to accept choices using a dict() for a label. The dict for each option must include
    'label' (string) and 'disabled' (boolean).
    """
    option_template_name = 'widgets/selectwithdisabled_option.html'


class StaticSelect(SelectWithDisabled):
    """
    A static <select/> form widget which is client-side rendered.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.attrs['class'] = 'netbox-static-select'


class StaticSelectMultiple(StaticSelect, forms.SelectMultiple):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.attrs['data-multiple'] = 1


class SelectWithPK(StaticSelect):
    """
    Include the primary key of each option in the option label (e.g. "Router7 (4721)").
    """
    option_template_name = 'widgets/select_option_with_pk.html'


class ContentTypeSelect(StaticSelect):
    """
    Appends an `api-value` attribute equal to the slugified model name for each ContentType. For example:
        <option value="37" api-value="console-server-port">console server port</option>
    This attribute can be used to reference the relevant API endpoint for a particular ContentType.
    """
    option_template_name = 'widgets/select_contenttype.html'


class SelectSpeedWidget(forms.NumberInput):
    """
    Speed field with dropdown selections for convenience.
    """
    template_name = 'widgets/select_speed.html'


class NumericArrayField(SimpleArrayField):

    def to_python(self, value):
        if not value:
            return []
        if isinstance(value, str):
            value = ','.join([str(n) for n in parse_numeric_range(value)])
        return super().to_python(value)


class APISelect(SelectWithDisabled):
    """
    A select widget populated via an API call

    :param api_url: API endpoint URL. Required if not set automatically by the parent field.
    """
    def __init__(self, api_url=None, full=False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.attrs['class'] = 'netbox-api-select'
        if api_url:
            self.attrs['data-url'] = '/{}{}'.format(settings.BASE_PATH, api_url.lstrip('/'))  # Inject BASE_PATH

    def add_query_param(self, key: str, value: JSONPrimitive) -> None:
        """
        Add a query parameter with a static value to the API request.
        """
        self.add_filter_fields({'accessor': key, 'field_name': key, 'default_value': value})

    def add_filter_fields(self, filter_fields: Union[Dict[str, JSONPrimitive], Sequence[Dict[str, JSONPrimitive]]]) -> None:
        """
        Add details about another form field, the value for which should
        be added to this APISelect's URL query parameters.

        :Example:

        ```python
        {
            'field_name': 'tenant_group',
            'accessor': 'tenant',
            'default_value': 1,
            'include_null': False,
        }
        ```

        :param filter_fields: Dict or list of dicts with the following properties:

               - accessor: The related field's property name. For example, on the
                           `Tenant`model, a related model might be `TenantGroup`. In
                           this case, `accessor` would be `group_id`.

               - field_name: The related field's form name. In the above `Tenant`
                             example, `field_name` would be `tenant_group`.

               - default_value: (Optional) Set a default initial value, which can be
                                overridden if the field changes.

               - include_null: (Optional) Include `null` on queries for the related
                               field. For example, if `True`, `?<fieldName>=null` will
                               be added to all API queries for this field.

        """
        key = 'data-filter-fields'
        # Deserialize the current serialized value from the widget, using an empty JSON
        # array as a fallback in the event one is not defined.
        current = json.loads(self.attrs.get(key, '[]'))

        # Create a new list of filter fields using camelCse to align with front-end code standards
        # (this value will be read and used heavily at the JavaScript layer).
        update: Sequence[Dict[str, str]] = []
        try:
            if isinstance(filter_fields, Sequence):
                update = [
                    {
                        'fieldName': field['field_name'],
                        'queryParam': field['accessor'],
                        'defaultValue': field.get('default_value'),
                        'includeNull': field.get('include_null', False),
                    } for field in filter_fields
                ]
            elif isinstance(filter_fields, Dict):
                update = [
                    {
                        'fieldName': filter_fields['field_name'],
                        'queryParam': filter_fields['accessor'],
                        'defaultValue': filter_fields.get('default_value'),
                        'includeNull': filter_fields.get('include_null', False),
                    }
                ]

        except KeyError as error:
            raise KeyError(f"Missing required property '{error.args[0]}' on APISelect.filter_fields") from error

        # Combine the current values with the updated values and serialize the result as
        # JSON. Note: the `separators` kwarg effectively removes extra whitespace from
        # the serialized JSON string, which is ideal since these will be passed as
        # attributes to HTML elements and parsed on the client.
        self.attrs[key] = json.dumps([*current, *update], separators=(',', ':'))


class APISelectMultiple(APISelect, forms.SelectMultiple):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.attrs['data-multiple'] = 1


class DatePicker(forms.TextInput):
    """
    Date picker using Flatpickr.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'date-picker'
        self.attrs['placeholder'] = 'YYYY-MM-DD'


class DateTimePicker(forms.TextInput):
    """
    DateTime picker using Flatpickr.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'datetime-picker'
        self.attrs['placeholder'] = 'YYYY-MM-DD hh:mm:ss'


class TimePicker(forms.TextInput):
    """
    Time picker using Flatpickr.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs['class'] = 'time-picker'
        self.attrs['placeholder'] = 'hh:mm:ss'
