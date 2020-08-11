import json

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
    'SelectWithDisabled',
    'SelectWithPK',
    'SlugWidget',
    'SmallTextarea',
    'StaticSelect2',
    'StaticSelect2Multiple',
    'TimePicker',
)


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
        self.attrs['class'] = 'netbox-select2-color-picker'


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
        self.attrs['class'] = 'netbox-select2-static'


class SelectWithDisabled(forms.Select):
    """
    Modified the stock Select widget to accept choices using a dict() for a label. The dict for each option must include
    'label' (string) and 'disabled' (boolean).
    """
    option_template_name = 'widgets/selectwithdisabled_option.html'


class StaticSelect2(SelectWithDisabled):
    """
    A static content using the Select2 widget

    :param filter_for: (Optional) A dict of chained form fields for which this field is a filter. The key is the
        name of the filter-for field (child field) and the value is the name of the query param filter.
    """

    def __init__(self, filter_for=None, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.attrs['class'] = 'netbox-select2-static'
        if filter_for:
            for key, value in filter_for.items():
                self.add_filter_for(key, value)

    def add_filter_for(self, name, value):
        """
        Add details for an additional query param in the form of a data-filter-for-* attribute.

        :param name: The name of the query param
        :param value: The value of the query param
        """
        self.attrs['data-filter-for-{}'.format(name)] = value


class StaticSelect2Multiple(StaticSelect2, forms.SelectMultiple):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.attrs['data-multiple'] = 1


class SelectWithPK(StaticSelect2):
    """
    Include the primary key of each option in the option label (e.g. "Router7 (4721)").
    """
    option_template_name = 'widgets/select_option_with_pk.html'


class ContentTypeSelect(StaticSelect2):
    """
    Appends an `api-value` attribute equal to the slugified model name for each ContentType. For example:
        <option value="37" api-value="console-server-port">console server port</option>
    This attribute can be used to reference the relevant API endpoint for a particular ContentType.
    """
    option_template_name = 'widgets/select_contenttype.html'


class NumericArrayField(SimpleArrayField):

    def to_python(self, value):
        value = ','.join([str(n) for n in parse_numeric_range(value)])
        return super().to_python(value)


class APISelect(SelectWithDisabled):
    """
    A select widget populated via an API call

    :param api_url: API endpoint URL. Required if not set automatically by the parent field.
    :param display_field: (Optional) Field to display for child in selection list. Defaults to `name`.
    :param value_field: (Optional) Field to use for the option value in selection list. Defaults to `id`.
    :param disabled_indicator: (Optional) Mark option as disabled if this field equates true.
    :param filter_for: (Optional) A dict of chained form fields for which this field is a filter. The key is the
        name of the filter-for field (child field) and the value is the name of the query param filter.
    :param conditional_query_params: (Optional) A dict of URL query params to append to the URL if the
        condition is met. The condition is the dict key and is specified in the form `<field_name>__<field_value>`.
        If the provided field value is selected for the given field, the URL query param will be appended to
        the rendered URL. The value is the in the from `<param_name>=<param_value>`. This is useful in cases where
        a particular field value dictates an additional API filter.
    :param additional_query_params: Optional) A dict of query params to append to the API request. The key is the
        name of the query param and the value if the query param's value.
    :param null_option: If true, include the static null option in the selection list.
    """
    def __init__(
        self,
        api_url=None,
        display_field=None,
        value_field=None,
        disabled_indicator=None,
        filter_for=None,
        conditional_query_params=None,
        additional_query_params=None,
        null_option=False,
        full=False,
        *args,
        **kwargs
    ):

        super().__init__(*args, **kwargs)

        self.attrs['class'] = 'netbox-select2-api'
        if api_url:
            self.attrs['data-url'] = '/{}{}'.format(settings.BASE_PATH, api_url.lstrip('/'))  # Inject BASE_PATH
        if full:
            self.attrs['data-full'] = full
        if display_field:
            self.attrs['display-field'] = display_field
        if value_field:
            self.attrs['value-field'] = value_field
        if disabled_indicator:
            self.attrs['disabled-indicator'] = disabled_indicator
        if filter_for:
            for key, value in filter_for.items():
                self.add_filter_for(key, value)
        if conditional_query_params:
            for key, value in conditional_query_params.items():
                self.add_conditional_query_param(key, value)
        if additional_query_params:
            for key, value in additional_query_params.items():
                self.add_additional_query_param(key, value)
        if null_option:
            self.attrs['data-null-option'] = 1

    def add_filter_for(self, name, value):
        """
        Add details for an additional query param in the form of a data-filter-for-* attribute.

        :param name: The name of the query param
        :param value: The value of the query param
        """
        self.attrs['data-filter-for-{}'.format(name)] = value

    def add_additional_query_param(self, name, value):
        """
        Add details for an additional query param in the form of a data-* JSON-encoded list attribute.

        :param name: The name of the query param
        :param value: The value of the query param
        """
        key = 'data-additional-query-param-{}'.format(name)

        values = json.loads(self.attrs.get(key, '[]'))
        values.append(value)

        self.attrs[key] = json.dumps(values)

    def add_conditional_query_param(self, condition, value):
        """
        Add details for a URL query strings to append to the URL if the condition is met.
        The condition is specified in the form `<field_name>__<field_value>`.

        :param condition: The condition for the query param
        :param value: The value of the query param
        """
        self.attrs['data-conditional-query-param-{}'.format(condition)] = value


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
