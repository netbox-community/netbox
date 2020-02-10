import csv
import json
import re
from io import StringIO
import yaml

from django import forms
from django.conf import settings
from django.contrib.postgres.forms.jsonb import JSONField as _JSONField, InvalidJSONInput
from django.db.models import Count
from django.forms import BoundField

from .choices import unpack_grouped_choices
from .constants import *
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


#
# Widgets
#

class SmallTextarea(forms.Textarea):
    """
    Subclass used for rendering a smaller textarea element.
    """
    pass


class ColorSelect(forms.Select):
    """
    Extends the built-in Select widget to colorize each <option>.
    """
    option_template_name = 'widgets/colorselect_option.html'

    def __init__(self, *args, **kwargs):
        kwargs['choices'] = add_blank_choice(COLOR_CHOICES)
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


class ArrayFieldSelectMultiple(SelectWithDisabled, forms.SelectMultiple):
    """
    MultiSelect widget for a SimpleArrayField. Choices must be populated on the widget.
    """
    def __init__(self, *args, **kwargs):
        self.delimiter = kwargs.pop('delimiter', ',')
        super().__init__(*args, **kwargs)

    def optgroups(self, name, value, attrs=None):
        # Split the delimited string of values into a list
        if value:
            value = value[0].split(self.delimiter)
        return super().optgroups(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        # Condense the list of selected choices into a delimited string
        data = super().value_from_datadict(data, files, name)
        return self.delimiter.join(data)


class APISelect(SelectWithDisabled):
    """
    A select widget populated via an API call

    :param api_url: API URL
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
        api_url,
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
        Add details for an additional query param in the form of a data-* attribute.

        :param name: The name of the query param
        :param value: The value of the query param
        """
        self.attrs['data-additional-query-param-{}'.format(name)] = value

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
    A CharField (rendered as a Textarea) which accepts CSV-formatted data. It returns a list of dictionaries mapping
    column headers to values. Each dictionary represents an individual record.
    """
    widget = forms.Textarea

    def __init__(self, fields, required_fields=[], *args, **kwargs):

        self.fields = fields
        self.required_fields = required_fields

        super().__init__(*args, **kwargs)

        self.strip = False
        if not self.label:
            self.label = ''
        if not self.initial:
            self.initial = ','.join(required_fields) + '\n'
        if not self.help_text:
            self.help_text = 'Enter the list of column headers followed by one line per record to be imported, using ' \
                             'commas to separate values. Multi-line data and values containing commas may be wrapped ' \
                             'in double quotes.'

    def to_python(self, value):

        records = []
        reader = csv.reader(StringIO(value))

        # Consume and validate the first line of CSV data as column headers
        headers = next(reader)
        for f in self.required_fields:
            if f not in headers:
                raise forms.ValidationError('Required column header "{}" not found.'.format(f))
        for f in headers:
            if f not in self.fields:
                raise forms.ValidationError('Unexpected column header "{}" found.'.format(f))

        # Parse CSV data
        for i, row in enumerate(reader, start=1):
            if row:
                if len(row) != len(headers):
                    raise forms.ValidationError(
                        "Row {}: Expected {} columns but found {}".format(i, len(headers), len(row))
                    )
                row = [col.strip() for col in row]
                record = dict(zip(headers, row))
                records.append(record)

        return records


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
    A textarea with support for GitHub-Flavored Markdown. Exists mostly just to add a standard help_text.
    """
    widget = forms.Textarea
    default_label = ''
    # TODO: Port GFM syntax cheat sheet to internal documentation
    default_helptext = '<i class="fa fa-info-circle"></i> '\
                       '<a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet" target="_blank">'\
                       'GitHub-Flavored Markdown</a> syntax is supported'

    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)
        label = kwargs.pop('label', self.default_label)
        help_text = kwargs.pop('help_text', self.default_helptext)
        super().__init__(required=required, label=label, help_text=help_text, *args, **kwargs)


class FlexibleModelChoiceField(forms.ModelChoiceField):
    """
    Allow a model to be reference by either '{ID}' or the field specified by `to_field_name`.
    """
    def to_python(self, value):
        if value in self.empty_values:
            return None
        try:
            if not self.to_field_name:
                key = 'pk'
            elif re.match(r'^\{\d+\}$', value):
                key = 'pk'
                value = value.strip('{}')
            else:
                key = self.to_field_name
            value = self.queryset.get(**{key: value})
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise forms.ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value


class SlugField(forms.SlugField):
    """
    Extend the built-in SlugField to automatically populate from a field called `name` unless otherwise specified.
    """
    def __init__(self, slug_source='name', *args, **kwargs):
        label = kwargs.pop('label', "Slug")
        help_text = kwargs.pop('help_text', "URL-friendly unique shorthand")
        super().__init__(label=label, help_text=help_text, *args, **kwargs)
        self.widget.attrs['slug-source'] = slug_source


class TagFilterField(forms.MultipleChoiceField):
    """
    A filter field for the tags of a model. Only the tags used by a model are displayed.

    :param model: The model of the filter
    """
    widget = StaticSelect2Multiple

    def __init__(self, model, *args, **kwargs):
        def get_choices():
            tags = model.tags.annotate(count=Count('extras_taggeditem_items')).order_by('name')
            return [(str(tag.slug), '{} ({})'.format(tag.name, tag.count)) for tag in tags]

        # Choices are fetched each time the form is initialized
        super().__init__(label='Tags', choices=get_choices, required=False, *args, **kwargs)


class DynamicModelChoiceField(forms.ModelChoiceField):
    """
    Override get_bound_field() to avoid pre-populating field choices with a SQL query. The field will be
    rendered only with choices set via bound data. Choices are populated on-demand via the APISelect widget.
    """
    field_modifier = ''

    def get_bound_field(self, form, field_name):
        bound_field = BoundField(form, self, field_name)

        # Modify the QuerySet of the field before we return it. Limit choices to any data already bound: Options
        # will be populated on-demand via the APISelect widget.
        if bound_field.data:
            field_name = '{}{}'.format(self.to_field_name or 'pk', self.field_modifier)
            kwargs = {field_name: bound_field.data}
            self.queryset = self.queryset.filter(**kwargs)
        else:
            self.queryset = self.queryset.none()

        return bound_field


class DynamicModelMultipleChoiceField(DynamicModelChoiceField):
    """
    A multiple-choice version of DynamicModelChoiceField.
    """
    field_modifier = '__in'


class FilterChoiceField(DynamicModelMultipleChoiceField):
    """
    A version of DynamicModelMultipleChoiceField which defaults to required=False.
    """
    def __init__(self, *args, **kwargs):
        # Filter fields are not required by default
        if 'required' not in kwargs:
            kwargs['required'] = False
        super().__init__(*args, **kwargs)


class LaxURLField(forms.URLField):
    """
    Modifies Django's built-in URLField in two ways:
      1) Allow any valid scheme per RFC 3986 section 3.1
      2) Remove the requirement for fully-qualified domain names (e.g. http://myserver/ is valid)
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
            forms.CheckboxInput, forms.ClearableFileInput, forms.FileInput, forms.RadioSelect
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


class ImportForm(BootstrapMixin, forms.Form):
    """
    Generic form for creating an object from JSON/YAML data
    """
    data = forms.CharField(
        widget=forms.Textarea,
        help_text="Enter object data in JSON or YAML format."
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
            except json.decoder.JSONDecodeError as err:
                raise forms.ValidationError({
                    'data': "Invalid JSON data: {}".format(err)
                })
        else:
            try:
                self.cleaned_data['data'] = yaml.load(data, Loader=yaml.SafeLoader)
            except yaml.scanner.ScannerError as err:
                raise forms.ValidationError({
                    'data': "Invalid YAML data: {}".format(err)
                })
