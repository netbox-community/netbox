import csv
import json
import re
from io import StringIO

import django_filters
import yaml
from django import forms
from django.conf import settings
from django.contrib.postgres.forms import SimpleArrayField
from django.contrib.postgres.forms.jsonb import JSONField as _JSONField, InvalidJSONInput
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Count
from django.forms import BoundField
from django.forms.models import fields_for_model
from django.urls import reverse

from utilities.querysets import RestrictedQuerySet
from .choices import ColorChoices, unpack_grouped_choices
from .validators import EnhancedURLValidator

NUMERIC_EXPANSION_PATTERN = r'\[((?:\d+[?:,-])+\d+)\]'
ALPHANUMERIC_EXPANSION_PATTERN = r'\[((?:[a-zA-Z0-9]+[?:,-])+[a-zA-Z0-9]+)\]'
IP4_EXPANSION_PATTERN = r'\[((?:[0-9]{1,3}[?:,-])+[0-9]{1,3})\]'
IP6_EXPANSION_PATTERN = r'\[((?:[0-9a-f]{1,4}[?:,-])+[0-9a-f]{1,4})\]'
BOOLEAN_WITH_BLANK_CHOICES = (
    ('', '---------'),
    ('True', 'Yes'),
    ('False', 'No'),
)


def parse_numeric_range(string, base=10):
    """
    Expand a numeric range (continuous or not) into a decimal or
    hexadecimal list, as specified by the base parameter
      '0-3,5' => [0, 1, 2, 3, 5]
      '2,8-b,d,f' => [2, 8, 9, a, b, d, f]
    """
    values = list()
    for dash_range in string.split(','):
        try:
            begin, end = dash_range.split('-')
        except ValueError:
            begin, end = dash_range, dash_range
        begin, end = int(begin.strip(), base=base), int(end.strip(), base=base) + 1
        values.extend(range(begin, end))
    return list(set(values))


def parse_alphanumeric_range(string):
    """
    Expand an alphanumeric range (continuous or not) into a list.
    'a-d,f' => [a, b, c, d, f]
    '0-3,a-d' => [0, 1, 2, 3, a, b, c, d]
    """
    values = []
    for dash_range in string.split(','):
        try:
            begin, end = dash_range.split('-')
            vals = begin + end
            # Break out of loop if there's an invalid pattern to return an error
            if (not (vals.isdigit() or vals.isalpha())) or (vals.isalpha() and not (vals.isupper() or vals.islower())):
                return []
        except ValueError:
            begin, end = dash_range, dash_range
        if begin.isdigit() and end.isdigit():
            for n in list(range(int(begin), int(end) + 1)):
                values.append(n)
        else:
            # Value-based
            if begin == end:
                values.append(begin)
            # Range-based
            else:
                # Not a valid range (more than a single character)
                if not len(begin) == len(end) == 1:
                    raise forms.ValidationError('Range "{}" is invalid.'.format(dash_range))
                for n in list(range(ord(begin), ord(end) + 1)):
                    values.append(chr(n))
    return values


def expand_alphanumeric_pattern(string):
    """
    Expand an alphabetic pattern into a list of strings.
    """
    lead, pattern, remnant = re.split(ALPHANUMERIC_EXPANSION_PATTERN, string, maxsplit=1)
    parsed_range = parse_alphanumeric_range(pattern)
    for i in parsed_range:
        if re.search(ALPHANUMERIC_EXPANSION_PATTERN, remnant):
            for string in expand_alphanumeric_pattern(remnant):
                yield "{}{}{}".format(lead, i, string)
        else:
            yield "{}{}{}".format(lead, i, remnant)


def expand_ipaddress_pattern(string, family):
    """
    Expand an IP address pattern into a list of strings. Examples:
      '192.0.2.[1,2,100-250]/24' => ['192.0.2.1/24', '192.0.2.2/24', '192.0.2.100/24' ... '192.0.2.250/24']
      '2001:db8:0:[0,fd-ff]::/64' => ['2001:db8:0:0::/64', '2001:db8:0:fd::/64', ... '2001:db8:0:ff::/64']
    """
    if family not in [4, 6]:
        raise Exception("Invalid IP address family: {}".format(family))
    if family == 4:
        regex = IP4_EXPANSION_PATTERN
        base = 10
    else:
        regex = IP6_EXPANSION_PATTERN
        base = 16
    lead, pattern, remnant = re.split(regex, string, maxsplit=1)
    parsed_range = parse_numeric_range(pattern, base)
    for i in parsed_range:
        if re.search(regex, remnant):
            for string in expand_ipaddress_pattern(remnant, family):
                yield ''.join([lead, format(i, 'x' if family == 6 else 'd'), string])
        else:
            yield ''.join([lead, format(i, 'x' if family == 6 else 'd'), remnant])


def add_blank_choice(choices):
    """
    Add a blank choice to the beginning of a choices list.
    """
    return ((None, '---------'),) + tuple(choices)


def form_from_model(model, fields):
    """
    Return a Form class with the specified fields derived from a model. This is useful when we need a form to be used
    for creating objects, but want to avoid the model's validation (e.g. for bulk create/edit functions). All fields
    are marked as not required.
    """
    form_fields = fields_for_model(model, fields=fields)
    for field in form_fields.values():
        field.required = False

    return type('FormFromModel', (forms.Form,), form_fields)


def restrict_form_fields(form, user, action='view'):
    """
    Restrict all form fields which reference a RestrictedQuerySet. This ensures that users see only permitted objects
    as available choices.
    """
    for field in form.fields.values():
        if hasattr(field, 'queryset') and issubclass(field.queryset.__class__, RestrictedQuerySet):
            field.queryset = field.queryset.restrict(user, action)


#
# Widgets
#

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


#
# Form fields
#

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
            self.help_text = 'Enter the list of column headers followed by one line per record to be imported, using ' \
                             'commas to separate values. Multi-line data and values containing commas may be wrapped ' \
                             'in double quotes.'

    def to_python(self, value):

        records = []
        reader = csv.reader(StringIO(value.strip()))

        # Consume the first line of CSV data as column headers. Create a dictionary mapping each header to an optional
        # "to" field specifying how the related object is being referenced. For example, importing a Device might use a
        # `site.slug` header, to indicate the related site is being referenced by its slug.
        headers = {}
        for header in next(reader):
            if '.' in header:
                field, to_field = header.split('.', 1)
                headers[field] = to_field
            else:
                headers[header] = None

        # Parse CSV rows into a list of dictionaries mapped from the column headers.
        for i, row in enumerate(reader, start=1):
            if len(row) != len(headers):
                raise forms.ValidationError(
                    f"Row {i}: Expected {len(headers)} columns but found {len(row)}"
                )
            row = [col.strip() for col in row]
            record = dict(zip(headers.keys(), row))
            records.append(record)

        return headers, records

    def validate(self, value):
        headers, records = value

        # Validate provided column headers
        for field, to_field in headers.items():
            if field not in self.fields:
                raise forms.ValidationError(f'Unexpected column header "{field}" found.')
            if to_field and not hasattr(self.fields[field], 'to_field_name'):
                raise forms.ValidationError(f'Column "{field}" is not a related object; cannot use dots')
            if to_field and not hasattr(self.fields[field].queryset.model, to_field):
                raise forms.ValidationError(f'Invalid related object attribute for column "{field}": {to_field}')

        # Validate required fields
        for f in self.required_fields:
            if f not in headers:
                raise forms.ValidationError(f'Required column header "{f}" not found.')

        return value


class CSVChoiceField(forms.ChoiceField):
    """
    Invert the provided set of choices to take the human-friendly label as input, and return the database value.
    """
    def __init__(self, choices, *args, **kwargs):
        super().__init__(choices=choices, *args, **kwargs)
        self.choices = [(label, label) for value, label in unpack_grouped_choices(choices)]
        self.choice_values = {label: value for value, label in unpack_grouped_choices(choices)}

    def clean(self, value):
        value = super().clean(value)
        if not value:
            return ''
        if value not in self.choice_values:
            raise forms.ValidationError("Invalid choice: {}".format(value))
        return self.choice_values[value]


class CSVModelChoiceField(forms.ModelChoiceField):
    """
    Provides additional validation for model choices entered as CSV data.
    """
    default_error_messages = {
        'invalid_choice': 'Object not found.',
    }

    def to_python(self, value):
        try:
            return super().to_python(value)
        except MultipleObjectsReturned as e:
            raise forms.ValidationError(
                f'"{value}" is not a unique value for this field; multiple objects were found'
            )


class ExpandableNameField(forms.CharField):
    """
    A field which allows for numeric range expansion
      Example: 'Gi0/[1-3]' => ['Gi0/1', 'Gi0/2', 'Gi0/3']
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.help_text:
            self.help_text = """
                Alphanumeric ranges are supported for bulk creation. Mixed cases and types within a single range
                are not supported. Examples:
                <ul>
                    <li><code>[ge,xe]-0/0/[0-9]</code></li>
                    <li><code>e[0-3][a-d,f]</code></li>
                </ul>
                """

    def to_python(self, value):
        if not value:
            return ''
        if re.search(ALPHANUMERIC_EXPANSION_PATTERN, value):
            return list(expand_alphanumeric_pattern(value))
        return [value]


class ExpandableIPAddressField(forms.CharField):
    """
    A field which allows for expansion of IP address ranges
      Example: '192.0.2.[1-254]/24' => ['192.0.2.1/24', '192.0.2.2/24', '192.0.2.3/24' ... '192.0.2.254/24']
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.help_text:
            self.help_text = 'Specify a numeric range to create multiple IPs.<br />'\
                             'Example: <code>192.0.2.[1,5,100-254]/24</code>'

    def to_python(self, value):
        # Hackish address family detection but it's all we have to work with
        if '.' in value and re.search(IP4_EXPANSION_PATTERN, value):
            return list(expand_ipaddress_pattern(value, 4))
        elif ':' in value and re.search(IP6_EXPANSION_PATTERN, value):
            return list(expand_ipaddress_pattern(value, 6))
        return [value]


class CommentField(forms.CharField):
    """
    A textarea with support for Markdown rendering. Exists mostly just to add a standard help_text.
    """
    widget = forms.Textarea
    default_label = ''
    # TODO: Port Markdown cheat sheet to internal documentation
    default_helptext = '<i class="fa fa-info-circle"></i> '\
                       '<a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet" target="_blank">'\
                       'Markdown</a> syntax is supported'

    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)
        label = kwargs.pop('label', self.default_label)
        help_text = kwargs.pop('help_text', self.default_helptext)
        super().__init__(required=required, label=label, help_text=help_text, *args, **kwargs)


class SlugField(forms.SlugField):
    """
    Extend the built-in SlugField to automatically populate from a field called `name` unless otherwise specified.
    """
    def __init__(self, slug_source='name', *args, **kwargs):
        label = kwargs.pop('label', "Slug")
        help_text = kwargs.pop('help_text', "URL-friendly unique shorthand")
        widget = kwargs.pop('widget', SlugWidget)
        super().__init__(label=label, help_text=help_text, widget=widget, *args, **kwargs)
        self.widget.attrs['slug-source'] = slug_source


class TagFilterField(forms.MultipleChoiceField):
    """
    A filter field for the tags of a model. Only the tags used by a model are displayed.

    :param model: The model of the filter
    """
    widget = StaticSelect2Multiple

    def __init__(self, model, *args, **kwargs):
        def get_choices():
            tags = model.tags.all().unrestricted().annotate(
                count=Count('extras_taggeditem_items')
            ).order_by('name')
            return [
                (str(tag.slug), '{} ({})'.format(tag.name, tag.count)) for tag in tags
            ]

        # Choices are fetched each time the form is initialized
        super().__init__(label='Tags', choices=get_choices, required=False, *args, **kwargs)


class DynamicModelChoiceMixin:
    filter = django_filters.ModelChoiceFilter
    widget = APISelect

    def _get_initial_value(self, initial_data, field_name):
        return initial_data.get(field_name)

    def get_bound_field(self, form, field_name):
        bound_field = BoundField(form, self, field_name)

        # Override initial() to allow passing multiple values
        bound_field.initial = self._get_initial_value(form.initial, field_name)

        # Modify the QuerySet of the field before we return it. Limit choices to any data already bound: Options
        # will be populated on-demand via the APISelect widget.
        data = bound_field.value()
        if data:
            filter = self.filter(field_name=self.to_field_name or 'pk', queryset=self.queryset)
            self.queryset = filter.filter(self.queryset, data)
        else:
            self.queryset = self.queryset.none()

        # Set the data URL on the APISelect widget (if not already set)
        widget = bound_field.field.widget
        if not widget.attrs.get('data-url'):
            app_label = self.queryset.model._meta.app_label
            model_name = self.queryset.model._meta.model_name
            data_url = reverse('{}-api:{}-list'.format(app_label, model_name))
            widget.attrs['data-url'] = data_url

        return bound_field


class DynamicModelChoiceField(DynamicModelChoiceMixin, forms.ModelChoiceField):
    """
    Override get_bound_field() to avoid pre-populating field choices with a SQL query. The field will be
    rendered only with choices set via bound data. Choices are populated on-demand via the APISelect widget.
    """
    pass


class DynamicModelMultipleChoiceField(DynamicModelChoiceMixin, forms.ModelMultipleChoiceField):
    """
    A multiple-choice version of DynamicModelChoiceField.
    """
    filter = django_filters.ModelMultipleChoiceFilter
    widget = APISelectMultiple

    def _get_initial_value(self, initial_data, field_name):
        # If a QueryDict has been passed as initial form data, get *all* listed values
        if hasattr(initial_data, 'getlist'):
            return initial_data.getlist(field_name)
        return initial_data.get(field_name)


class LaxURLField(forms.URLField):
    """
    Modifies Django's built-in URLField to remove the requirement for fully-qualified domain names
    (e.g. http://myserver/ is valid)
    """
    default_validators = [EnhancedURLValidator()]


class JSONField(_JSONField):
    """
    Custom wrapper around Django's built-in JSONField to avoid presenting "null" as the default text.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.help_text:
            self.help_text = 'Enter context data in <a href="https://json.org/">JSON</a> format.'
            self.widget.attrs['placeholder'] = ''

    def prepare_value(self, value):
        if isinstance(value, InvalidJSONInput):
            return value
        if value is None:
            return ''
        return json.dumps(value, sort_keys=True, indent=4)


#
# Forms
#

class BootstrapMixin(forms.BaseForm):
    """
    Add the base Bootstrap CSS classes to form elements.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        exempt_widgets = [
            forms.CheckboxInput,
            forms.ClearableFileInput,
            forms.FileInput,
            forms.RadioSelect
        ]

        for field_name, field in self.fields.items():
            if field.widget.__class__ not in exempt_widgets:
                css = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = ' '.join([css, 'form-control']).strip()
            if field.required and not isinstance(field.widget, forms.FileInput):
                field.widget.attrs['required'] = 'required'
            if 'placeholder' not in field.widget.attrs:
                field.widget.attrs['placeholder'] = field.label


class ReturnURLForm(forms.Form):
    """
    Provides a hidden return URL field to control where the user is directed after the form is submitted.
    """
    return_url = forms.CharField(required=False, widget=forms.HiddenInput())


class ConfirmationForm(BootstrapMixin, ReturnURLForm):
    """
    A generic confirmation form. The form is not valid unless the confirm field is checked.
    """
    confirm = forms.BooleanField(required=True, widget=forms.HiddenInput(), initial=True)


class BulkEditForm(forms.Form):
    """
    Base form for editing multiple objects in bulk
    """
    def __init__(self, model, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.nullable_fields = []

        # Copy any nullable fields defined in Meta
        if hasattr(self.Meta, 'nullable_fields'):
            self.nullable_fields = self.Meta.nullable_fields


class BulkRenameForm(forms.Form):
    """
    An extendable form to be used for renaming objects in bulk.
    """
    find = forms.CharField()
    replace = forms.CharField()
    use_regex = forms.BooleanField(
        required=False,
        initial=True,
        label='Use regular expressions'
    )

    def clean(self):

        # Validate regular expression in "find" field
        if self.cleaned_data['use_regex']:
            try:
                re.compile(self.cleaned_data['find'])
            except re.error:
                raise forms.ValidationError({
                    'find': "Invalid regular expression"
                })


class CSVModelForm(forms.ModelForm):
    """
    ModelForm used for the import of objects in CSV format.
    """
    def __init__(self, *args, headers=None, **kwargs):
        super().__init__(*args, **kwargs)

        # Modify the model form to accommodate any customized to_field_name properties
        if headers:
            for field, to_field in headers.items():
                if to_field is not None:
                    self.fields[field].to_field_name = to_field


class ImportForm(BootstrapMixin, forms.Form):
    """
    Generic form for creating an object from JSON/YAML data
    """
    data = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter object data in JSON or YAML format. Note: Only a single object/document is supported."
    )
    format = forms.ChoiceField(
        choices=(
            ('json', 'JSON'),
            ('yaml', 'YAML')
        ),
        initial='yaml'
    )

    def clean(self):

        data = self.cleaned_data['data']
        format = self.cleaned_data['format']

        # Process JSON/YAML data
        if format == 'json':
            try:
                self.cleaned_data['data'] = json.loads(data)
                # Check for multiple JSON objects
                if type(self.cleaned_data['data']) is not dict:
                    raise forms.ValidationError({
                        'data': "Import is limited to one object at a time."
                    })
            except json.decoder.JSONDecodeError as err:
                raise forms.ValidationError({
                    'data': "Invalid JSON data: {}".format(err)
                })
        else:
            # Check for multiple YAML documents
            if '\n---' in data:
                raise forms.ValidationError({
                    'data': "Import is limited to one object at a time."
                })
            try:
                self.cleaned_data['data'] = yaml.load(data, Loader=yaml.SafeLoader)
            except yaml.error.YAMLError as err:
                raise forms.ValidationError({
                    'data': "Invalid YAML data: {}".format(err)
                })


class TableConfigForm(BootstrapMixin, forms.Form):
    """
    Form for configuring user's table preferences.
    """
    columns = forms.MultipleChoiceField(
        choices=[],
        widget=forms.SelectMultiple(
            attrs={'size': 10}
        ),
        help_text="Use the buttons below to arrange columns in the desired order, then select all columns to display."
    )

    def __init__(self, table, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize columns field based on table attributes
        self.fields['columns'].choices = table.configurable_columns
        self.fields['columns'].initial = table.visible_columns
