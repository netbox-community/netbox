import csv
import re

from django import forms
from django.core.urlresolvers import reverse_lazy
from django.utils.encoding import force_text
from django.utils.html import format_html
from django.utils.safestring import mark_safe


EXPANSION_PATTERN = '\[(\d+-\d+)\]'


def expand_pattern(string):
    """
    Expand a numeric pattern into a list of strings. Examples:
      'ge-0/0/[0-3]' => ['ge-0/0/0', 'ge-0/0/1', 'ge-0/0/2', 'ge-0/0/3']
      'xe-0/[0-3]/[0-7]' => ['xe-0/0/0', 'xe-0/0/1', 'xe-0/0/2', ... 'xe-0/3/5', 'xe-0/3/6', 'xe-0/3/7']
    """
    lead, pattern, remnant = re.split(EXPANSION_PATTERN, string, maxsplit=1)
    x, y = pattern.split('-')
    for i in range(int(x), int(y) + 1):
        if re.search(EXPANSION_PATTERN, remnant):
            for string in expand_pattern(remnant):
                yield "{}{}{}".format(lead, i, string)
        else:
            yield "{}{}{}".format(lead, i, remnant)


def add_blank_choice(choices):
    """
    Add a blank choice to the beginning of a choices list.
    """
    return ((None, '---------'),) + choices


#
# Widgets
#

class SmallTextarea(forms.Textarea):
    pass


class SelectWithDisabled(forms.Select):
    """
    Modified the stock Select widget to accept choices using a dict() for a label. The dict for each option must include
    'label' (string) and 'disabled' (boolean).
    """

    def render_option(self, selected_choices, option_value, option_label):

        # Determine if option has been selected
        option_value = force_text(option_value)
        if option_value in selected_choices:
            selected_html = mark_safe(' selected="selected"')
            if not self.allow_multiple_selected:
                # Only allow for a single selection.
                selected_choices.remove(option_value)
        else:
            selected_html = ''

        # Determine if option has been disabled
        option_disabled = False
        exempt_value = force_text(self.attrs.get('exempt', None))
        if isinstance(option_label, dict):
            option_disabled = option_label['disabled'] if option_value != exempt_value else False
            option_label = option_label['label']
        disabled_html = ' disabled="disabled"' if option_disabled else ''

        return format_html(u'<option value="{}"{}{}>{}</option>',
                           option_value,
                           selected_html,
                           disabled_html,
                           force_text(option_label))


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
        self.attrs['api-url'] = api_url
        if display_field:
            self.attrs['display-field'] = display_field
        if disabled_indicator:
            self.attrs['disabled-indicator'] = disabled_indicator


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
    A field for comma-separated values (CSV). Values containing commas should be encased within double quotes. Example:
        '"New York, NY",new-york-ny,Other stuff' => ['New York, NY', 'new-york-ny', 'Other stuff']
    """
    csv_form = None
    widget = forms.Textarea

    def __init__(self, csv_form, *args, **kwargs):
        self.csv_form = csv_form
        self.columns = self.csv_form().fields.keys()
        super(CSVDataField, self).__init__(*args, **kwargs)
        self.strip = False
        if not self.label:
            self.label = 'CSV Data'
        if not self.help_text:
            self.help_text = 'Enter one line per record in CSV format.'

    def to_python(self, value):
        # Return a list of dictionaries, each representing an individual record
        records = []
        reader = csv.reader(value.splitlines())
        for i, row in enumerate(reader, start=1):
            if row:
                if len(row) < len(self.columns):
                    raise forms.ValidationError("Line {}: Field(s) missing (found {}; expected {})"
                                                .format(i, len(row), len(self.columns)))
                elif len(row) > len(self.columns):
                    raise forms.ValidationError("Line {}: Too many fields (found {}; expected {})"
                                                .format(i, len(row), len(self.columns)))
                record = dict(zip(self.columns, row))
                records.append(record)
        return records


class ExpandableNameField(forms.CharField):
    """
    A field which allows for numeric range expansion
      Example: 'Gi0/[1-3]' => ['Gi0/1', 'Gi0/2', 'Gi0/3']
    """
    def __init__(self, *args, **kwargs):
        super(ExpandableNameField, self).__init__(*args, **kwargs)
        if not self.help_text:
            self.help_text = 'Numeric ranges are supported for bulk creation.<br />'\
                             'Example: <code>ge-0/0/[0-47]</code>'

    def to_python(self, value):
        if re.search(EXPANSION_PATTERN, value):
            return list(expand_pattern(value))
        return [value]


class CommentField(forms.CharField):
    """
    A textarea with support for GitHub-Flavored Markdown. Exists mostly just to add a standard help_text.
    """
    widget = forms.Textarea
    # TODO: Port GFM syntax cheat sheet to internal documentation
    default_helptext = '<i class="fa fa-info-circle"></i> '\
                       '<a href="https://github.com/adam-p/markdown-here/wiki/Markdown-Cheatsheet" target="_blank">'\
                       'GitHub-Flavored Markdown</a> syntax is supported'

    def __init__(self, *args, **kwargs):
        required = kwargs.pop('required', False)
        help_text = kwargs.pop('help_text', self.default_helptext)
        super(CommentField, self).__init__(required=required, help_text=help_text, *args, **kwargs)


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
            elif re.match('^\{\d+\}$', value):
                key = 'pk'
                value = value.strip('{}')
            else:
                key = self.to_field_name
            value = self.queryset.get(**{key: value})
        except (ValueError, TypeError, self.queryset.model.DoesNotExist):
            raise forms.ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')
        return value


class SlugField(forms.SlugField):

    def __init__(self, slug_source='name', *args, **kwargs):
        label = kwargs.pop('label', "Slug")
        help_text = kwargs.pop('help_text', "URL-friendly unique shorthand")
        super(SlugField, self).__init__(label=label, help_text=help_text, *args, **kwargs)
        self.widget.attrs['slug-source'] = slug_source


#
# Forms
#

class BootstrapMixin(forms.BaseForm):

    def __init__(self, *args, **kwargs):
        super(BootstrapMixin, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if type(field.widget) not in [type(forms.CheckboxInput()), type(forms.RadioSelect())]:
                try:
                    field.widget.attrs['class'] += ' form-control'
                except KeyError:
                    field.widget.attrs['class'] = 'form-control'
            if field.required:
                field.widget.attrs['required'] = 'required'
            if 'placeholder' not in field.widget.attrs:
                field.widget.attrs['placeholder'] = field.label


class ConfirmationForm(forms.Form, BootstrapMixin):
    confirm = forms.BooleanField(required=True)


class BulkImportForm(forms.Form):

    def clean(self):
        records = self.cleaned_data.get('csv')
        if not records:
            return

        obj_list = []

        for i, record in enumerate(records, start=1):
            obj_form = self.fields['csv'].csv_form(data=record)
            if obj_form.is_valid():
                obj = obj_form.save(commit=False)
                obj_list.append(obj)
            else:
                for field, errors in obj_form.errors.items():
                    for e in errors:
                        if field == '__all__':
                            self.add_error('csv', "Record {}: {}".format(i, e))
                        else:
                            self.add_error('csv', "Record {} ({}): {}".format(i, field, e))

        self.cleaned_data['csv'] = obj_list
