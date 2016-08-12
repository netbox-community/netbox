import six

from django import forms
from django.contrib.contenttypes.models import ContentType

from .models import CF_TYPE_BOOLEAN, CF_TYPE_DATE, CF_TYPE_INTEGER, CF_TYPE_SELECT, CF_TYPE_TEXT, CustomField


class CustomFieldForm(forms.ModelForm):
    test_field = forms.IntegerField(widget=forms.HiddenInput())

    custom_fields = []

    def __init__(self, *args, **kwargs):

        super(CustomFieldForm, self).__init__(*args, **kwargs)

        # Find all CustomFields for this model
        model = self._meta.model
        custom_fields = CustomField.objects.filter(obj_type=ContentType.objects.get_for_model(model))

        for cf in custom_fields:

            field_name = 'cf_{}'.format(str(cf.name))

            # Integer
            if cf.type == CF_TYPE_INTEGER:
                field = forms.IntegerField(blank=not cf.required)

            # Boolean
            elif cf.type == CF_TYPE_BOOLEAN:
                if cf.required:
                    field = forms.BooleanField(required=False)
                else:
                    field = forms.NullBooleanField(required=False)

            # Date
            elif cf.type == CF_TYPE_DATE:
                field = forms.DateField(blank=not cf.required)

            # Select
            elif cf.type == CF_TYPE_SELECT:
                field = forms.ModelChoiceField(queryset=cf.choices.all(), required=cf.required)

            # Text
            else:
                field = forms.CharField(max_length=100, blank=not cf.required)

            field.label = cf.label if cf.label else cf.name
            field.help_text = cf.description
            self.fields[field_name] = field
            self.custom_fields.append(field_name)
