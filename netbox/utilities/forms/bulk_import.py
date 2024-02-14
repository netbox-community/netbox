import csv
import json
from io import StringIO

import yaml
from django import forms
from django.utils.translation import gettext as _

from core.forms.mixins import SyncedDataMixin
from utilities.choices import CSVDelimiterChoices, ImportFormatChoices, ImportMethodChoices
from utilities.constants import CSV_DELIMITERS
from utilities.forms.utils import parse_csv
from .mixins import BootstrapMixin


class BulkImportForm(BootstrapMixin, SyncedDataMixin, forms.Form):
    import_method = forms.ChoiceField(
        choices=ImportMethodChoices,
        required=False
    )
    data = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'font-monospace'}),
        help_text=_("Enter object data in CSV, JSON or YAML format.")
    )
    upload_file = forms.FileField(
        label=_("Data file"),
        required=False
    )
    format = forms.ChoiceField(
        choices=ImportFormatChoices,
        initial=ImportFormatChoices.AUTO
    )
    csv_delimiter = forms.ChoiceField(
        choices=CSVDelimiterChoices,
        initial=CSVDelimiterChoices.AUTO,
        label=_("CSV delimiter"),
        help_text=_("The character which delimits CSV fields. Applies only to CSV format."),
        required=False
    )

    data_field = 'data'

    def clean(self):
        super().clean()

        # Determine import method
        import_method = self.cleaned_data.get('import_method') or ImportMethodChoices.DIRECT

        # Determine whether we're reading from form data or an uploaded file
        if self.cleaned_data['data'] and import_method != ImportMethodChoices.DIRECT:
            raise forms.ValidationError(_("Form data must be empty when uploading/selecting a file."))
        if import_method == ImportMethodChoices.UPLOAD:
            self.upload_file = 'upload_file'
            file = self.files.get('upload_file')
            data = file.read().decode('utf-8-sig')
        elif import_method == ImportMethodChoices.DATA_FILE:
            data = self.cleaned_data['data_file'].data_as_string
        else:
            data = self.cleaned_data['data']

        # Determine the data format
        if self.cleaned_data['format'] == ImportFormatChoices.AUTO:
            if self.cleaned_data['csv_delimiter'] != CSVDelimiterChoices.AUTO:
                # Specifying the CSV delimiter implies CSV format
                format = ImportFormatChoices.CSV
            else:
                format = self._detect_format(data)
        else:
            format = self.cleaned_data['format']

        # Process data according to the selected format
        if format == ImportFormatChoices.CSV:
            delimiter = self.cleaned_data.get('csv_delimiter', CSVDelimiterChoices.AUTO)
            self.cleaned_data['data'] = self._clean_csv(data, delimiter=delimiter)
        elif format == ImportFormatChoices.JSON:
            self.cleaned_data['data'] = self._clean_json(data)
        elif format == ImportFormatChoices.YAML:
            self.cleaned_data['data'] = self._clean_yaml(data)
        else:
            raise forms.ValidationError(_("Unknown data format: {format}").format(format=format))

    def _detect_format(self, data):
        """
        Attempt to automatically detect the format (CSV, JSON, or YAML) of the given data, or raise
        a ValidationError.
        """
        try:
            if data[0] in ('{', '['):
                return ImportFormatChoices.JSON
            if data.startswith('---') or data.startswith('- '):
                return ImportFormatChoices.YAML
            # Look for any of the CSV delimiters in the first line (ignoring the default 'auto' choice)
            first_line = data.split('\n', 1)[0]
            csv_delimiters = CSV_DELIMITERS.values()
            if any(x in first_line for x in csv_delimiters):
                return ImportFormatChoices.CSV
        except IndexError:
            pass
        raise forms.ValidationError({
            'format': _('Unable to detect data format. Please specify.')
        })

    def _clean_csv(self, data, delimiter=CSVDelimiterChoices.AUTO):
        """
        Clean CSV-formatted data. The first row will be treated as column headers.
        """
        # Determine the CSV dialect
        if delimiter == CSVDelimiterChoices.AUTO:
            # This uses a rough heuristic to detect the CSV dialect based on the presence of supported delimiting
            # characters. If the data is malformed, we'll fall back to the default Excel dialect.
            delimiters = ''.join(CSV_DELIMITERS.values())
            try:
                dialect = csv.Sniffer().sniff(data.strip(), delimiters=delimiters)
            except csv.Error:
                dialect = csv.excel
        elif delimiter in (CSVDelimiterChoices.COMMA, CSVDelimiterChoices.SEMICOLON):
            dialect = csv.excel
            dialect.delimiter = delimiter
        elif delimiter == CSVDelimiterChoices.TAB:
            dialect = csv.excel_tab
        else:
            raise forms.ValidationError({
                'csv_delimiter': _('Invalid CSV delimiter'),
            })

        stream = StringIO(data.strip())
        reader = csv.reader(stream, dialect=dialect)
        headers, records = parse_csv(reader)

        # Set CSV headers for reference by the model form
        headers.pop('id', None)
        self._csv_headers = headers

        return records

    def _clean_json(self, data):
        """
        Clean JSON-formatted data. If only a single object is defined, it will be encapsulated as a list.
        """
        try:
            data = json.loads(data)
            # Accommodate for users entering single objects
            if type(data) is not list:
                data = [data]
            return data
        except json.decoder.JSONDecodeError as err:
            raise forms.ValidationError({
                self.data_field: f"Invalid JSON data: {err}"
            })

    def _clean_yaml(self, data):
        """
        Clean YAML-formatted data. Data must be either
          a) A single document comprising a list of dictionaries (each representing an object), or
          b) Multiple documents, separated with the '---' token
        """
        records = []
        try:
            for data in yaml.load_all(data, Loader=yaml.SafeLoader):
                if type(data) is list:
                    records.extend(data)
                elif type(data) is dict:
                    records.append(data)
                else:
                    raise forms.ValidationError({
                        self.data_field: _(
                            "Invalid YAML data. Data must be in the form of multiple documents, or a single document "
                            "comprising a list of dictionaries."
                        )
                    })
        except yaml.error.YAMLError as err:
            raise forms.ValidationError({
                self.data_field: f"Invalid YAML data: {err}"
            })

        return records
