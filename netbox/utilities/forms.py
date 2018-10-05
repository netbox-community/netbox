from __future__ import unicode_literals

import csv
from io import StringIO
import json
import re
import sys

from django import forms
from django.conf import settings
from django.contrib.postgres.forms.jsonb import JSONField as _JSONField, InvalidJSONInput
from django.db.models import Count
from django.urls import reverse_lazy
from mptt.forms import TreeNodeMultipleChoiceField

from .validators import EnhancedURLValidator

COLOR_CHOICES = (
    ('aa1409', 'Dark red'),
    ('f44336', 'Red'),
    ('e91e63', 'Pink'),
    ('ff66ff', 'Fuschia'),
    ('9c27b0', 'Purple'),
    ('673ab7', 'Dark purple'),
    ('3f51b5', 'Indigo'),
    ('2196f3', 'Blue'),
    ('03a9f4', 'Light blue'),
    ('00bcd4', 'Cyan'),
    ('009688', 'Teal'),
    ('2f6a31', 'Dark green'),
    ('4caf50', 'Green'),
    ('8bc34a', 'Light green'),
    ('cddc39', 'Lime'),
    ('ffeb3b', 'Yellow'),
    ('ffc107', 'Amber'),
    ('ff9800', 'Orange'),
    ('ff5722', 'Dark orange'),
    ('795548', 'Brown'),
    ('c0c0c0', 'Light grey'),
    ('9e9e9e', 'Grey'),
    ('607d8b', 'Dark grey'),
    ('111111', 'Black'),
)
NUMERIC_EXPANSION_PATTERN = r'\[((?:\d+[?:,-])+\d+)\]'
ALPHANUMERIC_EXPANSION_PATTERN = r'\[((?:[a-zA-Z0-9]+[?:,-])+[a-zA-Z0-9]+)\]'
IP4_EXPANSION_PATTERN = r'\[((?:[0-9]{1,3}[?:,-])+[0-9]{1,3})\]'
IP6_EXPANSION_PATTERN = r'\[((?:[0-9a-f]{1,4}[?:,-])+[0-9a-f]{1,4})\]'


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


def expand_numeric_pattern(string):
    """
    Expand a numeric pattern into a list of strings. Examples:
      'ge-0/0/[0-3,5]' => ['ge-0/0/0', 'ge-0/0/1', 'ge-0/0/2', 'ge-0/0/3', 'ge-0/0/5']
      'xe-0/[0,2-3]/[0-7]' => ['xe-0/0/0', 'xe-0/0/1', 'xe-0/0/2', ... 'xe-0/3/5', 'xe-0/3/6', 'xe-0/3/7']
    """
    lead, pattern, remnant = re.split(NUMERIC_EXPANSION_PATTERN, string, maxsplit=1)
    parsed_range = parse_numeric_range(pattern)
    for i in parsed_range:
        if re.search(NUMERIC_EXPANSION_PATTERN, remnant):
            for string in expand_numeric_pattern(remnant):
                yield "{}{}{}".format(lead, i, string)
        else:
            yield "{}{}{}".format(lead, i, remnant)


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
      '192.0.2.[1,2,100-250,254]/24' => ['192.0.2.1/24', '192.0.2.2/24', '192.0.2.100/24' ... '192.0.2.250/24', '192.0.2.254/24']
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


def utf8_encoder(data):
    for line in data:
        yield line.encode('utf-8')


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
        kwargs['choices'] = COLOR_CHOICES
        super(ColorSelect, self).__init__(*args, **kwargs)


class BulkEditNullBooleanSelect(forms.NullBooleanSelect):
    """
    A Select widget for NullBooleanFields
    """

    def __init__(self, *args, **kwargs):
        super(BulkEditNullBooleanSelect, self).__init__(*args, **kwargs)

        # Override the built-in choice labels
        self.choices = (
            ('1', '---------'),
            ('2', 'Yes'),
            ('3', 'No'),
        )


class SelectWithDisabled(forms.Select):
    """
    Modified the stock Select widget to accept choices using a dict() for a label. The dict for each option must include
    'label' (string) and 'disabled' (boolean).
    """
    option_template_name = 'widgets/selectwithdisabled_option.html'


class SelectWithPK(forms.Select):
    """
    Include the primary key of each option in the option label (e.g. "Router7 (4721)").
    """
    option_template_name = 'widgets/select_option_with_pk.html'


class ArrayFieldSelectMultiple(SelectWithDisabled, forms.SelectMultiple):
    """
    MultiSelect widget for a SimpleArrayField. Choices must be populated on the widget.
    """
    def __init__(self, *args, **kwargs):
        self.delimiter = kwargs.pop('delimiter', ',')
        super(ArrayFieldSelectMultiple, self).__init__(*args, **kwargs)

    def optgroups(self, name, value, attrs=None):
        # Split the delimited string of values into a list
        if value:
            value = value[0].split(self.delimiter)
        return super(ArrayFieldSelectMultiple, self).optgroups(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        # Condense the list of selected choices into a delimited string
        data = super(ArrayFieldSelectMultiple, self).value_from_datadict(data, files, name)
        return self.delimiter.join(data)


class APISelect(SelectWithDisabled):
    """
    A select widget populated via an API call

    :param api_url: API URL
    :param display_field: (Optional) Field to display for child in selection list. Defaults to `name`.
    :param disabled_indicator: (Optional) Mark option as disabled if this field equates true.
    """

    def __init__(self, api_url, display_field=None, disabled_indicator=None, *args, **kwargs):

        super(APISelect, self).__init__(*args, **kwargs)

        self.attrs['class'] = 'api-select'
        self.attrs['api-url'] = '/{}{}'.format(settings.BASE_PATH, api_url.lstrip('/'))  # Inject BASE_PATH
        if display_field:
            self.attrs['display-field'] = display_field
        if disabled_indicator:
            self.attrs['disabled-indicator'] = disabled_indicator


class APISelectMultiple(APISelect):
    allow_multiple_selected = True


class Livesearch(forms.TextInput):
    """
    A text widget that carries a few extra bits of data for use in AJAX-powered autocomplete search

    :param query_key: The name of the parameter to query against
    :param query_url: The name of the API URL to query
    :param field_to_update: The name of the "real" form field whose value is being set
    :param obj_label: The field to use as the option label (optional)
    """

    def __init__(self, query_key, query_url, field_to_update, obj_label=None, *args, **kwargs):

        super(Livesearch, self).__init__(*args, **kwargs)

        self.attrs = {
            'data-key': query_key,
            'data-source': reverse_lazy(query_url),
            'data-field': field_to_update,
        }

        if obj_label:
            self.attrs['data-label'] = obj_label


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

        super(CSVDataField, self).__init__(*args, **kwargs)

        self.strip = False
        if not self.label:
            self.label = 'CSV Data'
        if not self.initial:
            self.initial = ','.join(required_fields) + '\n'
        if not self.help_text:
            self.help_text = 'Enter the list of column headers followed by one line per record to be imported, using ' \
                             'commas to separate values. Multi-line data and values containing commas may be wrapped ' \
                             'in double quotes.'

    def to_python(self, value):

        records = []

        # Python 2 hack for Unicode support in the CSV reader
        if sys.version_info[0] < 3:
            reader = csv.reader(utf8_encoder(StringIO(value)))
        else:
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
        super(CSVChoiceField, self).__init__(choices=choices, *args, **kwargs)
        self.choices = [(label, label) for value, label in choices]
        self.choice_values = {label: value for value, label in choices}

    def clean(self, value):
        value = super(CSVChoiceField, self).clean(value)
        if not value:
            return None
        if value not in self.choice_values:
            raise forms.ValidationError("Invalid choice: {}".format(value))
        return self.choice_values[value]


class ExpandableNameField(forms.CharField):
    """
    A field which allows for numeric range expansion
      Example: 'Gi0/[1-3]' => ['Gi0/1', 'Gi0/2', 'Gi0/3']
    """
    def __init__(self, *args, **kwargs):
        super(ExpandableNameField, self).__init__(*args, **kwargs)
        if not self.help_text:
            self.help_text = 'Alphanumeric ranges are supported for bulk creation.<br />' \
                             'Mixed cases and types within a single range are not supported.<br />' \
                             'Examples:<ul><li><code>ge-0/0/[0-23,25,30]</code></li>' \
                             '<li><code>e[0-3][a-d,f]</code></li>' \
                             '<li><code>e[0-3,a-d,f]</code></li></ul>'

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
        super(ExpandableIPAddressField, self).__init__(*args, **kwargs)
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
    default_label = 'Comments'
    # TODO: Port GFM syntax cheat sheet to internal documentation
    default_helptext = '<i class="fa fa-info-circle"></i> '\
                       '<a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet" target="_blank">'\
                       'GitHub-Flavored Markdown</a> syntax is supported'

    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)
        label = kwargs.pop('label', self.default_label)
        help_text = kwargs.pop('help_text', self.default_helptext)
        super(CommentField, self).__init__(required=required, label=label, help_text=help_text, *args, **kwargs)


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


class ChainedModelChoiceField(forms.ModelChoiceField):
    """
    A ModelChoiceField which is initialized based on the values of other fields within a form. `chains` is a dictionary
    mapping of model fields to peer fields within the form. For example:

        country1 = forms.ModelChoiceField(queryset=Country.objects.all())
        city1 = ChainedModelChoiceField(queryset=City.objects.all(), chains={'country': 'country1'}

    The queryset of the `city1` field will be modified as

        .filter(country=<value>)

    where <value> is the value of the `country1` field. (Note: The form must inherit from ChainedFieldsMixin.)
    """
    def __init__(self, chains=None, *args, **kwargs):
        self.chains = chains
        super(ChainedModelChoiceField, self).__init__(*args, **kwargs)


class ChainedModelMultipleChoiceField(forms.ModelMultipleChoiceField):
    """
    See ChainedModelChoiceField
    """
    def __init__(self, chains=None, *args, **kwargs):
        self.chains = chains
        super(ChainedModelMultipleChoiceField, self).__init__(*args, **kwargs)


class SlugField(forms.SlugField):
    """
    Extend the built-in SlugField to automatically populate from a field called `name` unless otherwise specified.
    """
    def __init__(self, slug_source='name', *args, **kwargs):
        label = kwargs.pop('label', "Slug")
        help_text = kwargs.pop('help_text', "URL-friendly unique shorthand")
        super(SlugField, self).__init__(label=label, help_text=help_text, *args, **kwargs)
        self.widget.attrs['slug-source'] = slug_source


class FilterChoiceIterator(forms.models.ModelChoiceIterator):

    def __iter__(self):
        # Filter on "empty" choice using FILTERS_NULL_CHOICE_VALUE (instead of an empty string)
        if self.field.null_label is not None:
            yield (settings.FILTERS_NULL_CHOICE_VALUE, self.field.null_label)
        queryset = self.queryset.all()
        # Can't use iterator() when queryset uses prefetch_related()
        if not queryset._prefetch_related_lookups:
            queryset = queryset.iterator()
        for obj in queryset:
            yield self.choice(obj)


class FilterChoiceFieldMixin(object):
    iterator = FilterChoiceIterator

    def __init__(self, null_label=None, *args, **kwargs):
        self.null_label = null_label
        if 'required' not in kwargs:
            kwargs['required'] = False
        if 'widget' not in kwargs:
            kwargs['widget'] = forms.SelectMultiple(attrs={'size': 6})
        super(FilterChoiceFieldMixin, self).__init__(*args, **kwargs)

    def label_from_instance(self, obj):
        label = super(FilterChoiceFieldMixin, self).label_from_instance(obj)
        if hasattr(obj, 'filter_count'):
            return '{} ({})'.format(label, obj.filter_count)
        return label


class FilterChoiceField(FilterChoiceFieldMixin, forms.ModelMultipleChoiceField):
    pass


class FilterTreeNodeMultipleChoiceField(FilterChoiceFieldMixin, TreeNodeMultipleChoiceField):
    pass


class AnnotatedMultipleChoiceField(forms.MultipleChoiceField):
    """
    Render a set of static choices with each choice annotated to include a count of related objects. For example, this
    field can be used to display a list of all available device statuses along with the number of devices currently
    assigned to each status.
    """

    def annotate_choices(self):
        queryset = self.annotate.values(
            self.annotate_field
        ).annotate(
            count=Count(self.annotate_field)
        ).order_by(
            self.annotate_field
        )
        choice_counts = {
            c[self.annotate_field]: c['count'] for c in queryset
        }
        annotated_choices = [
            (c[0], '{} ({})'.format(c[1], choice_counts.get(c[0], 0))) for c in self.static_choices
        ]

        return annotated_choices

    def __init__(self, choices, annotate, annotate_field, *args, **kwargs):
        self.annotate = annotate
        self.annotate_field = annotate_field
        self.static_choices = choices

        super(AnnotatedMultipleChoiceField, self).__init__(choices=self.annotate_choices, *args, **kwargs)


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
        super(JSONField, self).__init__(*args, **kwargs)
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
        super(BootstrapMixin, self).__init__(*args, **kwargs)

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


class ChainedFieldsMixin(forms.BaseForm):
    """
    Iterate through all ChainedModelChoiceFields in the form and modify their querysets based on chained fields.
    """
    def __init__(self, *args, **kwargs):
        super(ChainedFieldsMixin, self).__init__(*args, **kwargs)

        for field_name, field in self.fields.items():

            if isinstance(field, ChainedModelChoiceField):

                filters_dict = {}
                for (db_field, parent_field) in field.chains:
                    if self.is_bound and parent_field in self.data:
                        filters_dict[db_field] = self.data[parent_field] or None
                    elif self.initial.get(parent_field):
                        filters_dict[db_field] = self.initial[parent_field]
                    elif self.fields[parent_field].widget.attrs.get('nullable'):
                        filters_dict[db_field] = None
                    else:
                        break

                if filters_dict:
                    field.queryset = field.queryset.filter(**filters_dict)
                elif not self.is_bound and getattr(self, 'instance', None) and hasattr(self.instance, field_name):
                    obj = getattr(self.instance, field_name)
                    if obj is not None:
                        field.queryset = field.queryset.filter(pk=obj.pk)
                    else:
                        field.queryset = field.queryset.none()
                elif not self.is_bound:
                    field.queryset = field.queryset.none()


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


class ComponentForm(BootstrapMixin, forms.Form):
    """
    Allow inclusion of the parent Device/VirtualMachine as context for limiting field choices.
    """
    def __init__(self, parent, *args, **kwargs):
        self.parent = parent
        super(ComponentForm, self).__init__(*args, **kwargs)


class BulkEditForm(forms.Form):
    """
    Base form for editing multiple objects in bulk
    """
    def __init__(self, model, parent_obj=None, *args, **kwargs):
        super(BulkEditForm, self).__init__(*args, **kwargs)
        self.model = model
        self.parent_obj = parent_obj
        self.nullable_fields = []

        # Copy any nullable fields defined in Meta
        if hasattr(self.Meta, 'nullable_fields'):
            self.nullable_fields = self.Meta.nullable_fields
