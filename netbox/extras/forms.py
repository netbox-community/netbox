from django import forms
from django.contrib.contenttypes.models import ContentType

from .models import CF_TYPE_BOOLEAN, CF_TYPE_DATE, CF_TYPE_INTEGER, CF_TYPE_SELECT, CustomField, CustomFieldValue


def get_custom_fields_for_model(content_type, bulk_editing=False):
    """
    Retrieve all CustomFields applicable to the given ContentType
    """
    field_dict = {}
    custom_fields = CustomField.objects.filter(obj_type=content_type)

    for cf in custom_fields:
        field_name = 'cf_{}'.format(str(cf.name))

        # Integer
        if cf.type == CF_TYPE_INTEGER:
            field = forms.IntegerField(required=cf.required, initial=cf.default)

        # Boolean
        elif cf.type == CF_TYPE_BOOLEAN:
            choices = (
                (None, '---------'),
                (True, 'True'),
                (False, 'False'),
            )
            field = forms.NullBooleanField(required=cf.required, widget=forms.Select(choices=choices))

        # Date
        elif cf.type == CF_TYPE_DATE:
            field = forms.DateField(required=cf.required, initial=cf.default)

        # Select
        elif cf.type == CF_TYPE_SELECT:
            choices = [(cfc.pk, cfc) for cfc in cf.choices.all()]
            if not cf.required:
                choices = [(0, 'None')] + choices
            if bulk_editing:
                choices = [(None, '---------')] + choices
                field = forms.TypedChoiceField(choices=choices, coerce=int, required=cf.required)
            else:
                field = forms.ModelChoiceField(queryset=cf.choices.all(), required=cf.required)

        # Text
        else:
            field = forms.CharField(max_length=255, required=cf.required, initial=cf.default)

        field.model = cf
        field.label = cf.label if cf.label else cf.name.capitalize()
        field.help_text = cf.description

        field_dict[field_name] = field

    return field_dict


class CustomFieldForm(forms.ModelForm):
    custom_fields = []

    def __init__(self, *args, **kwargs):

        self.obj_type = ContentType.objects.get_for_model(self._meta.model)

        super(CustomFieldForm, self).__init__(*args, **kwargs)

        # Add all applicable CustomFields to the form
        custom_fields = []
        for name, field in get_custom_fields_for_model(self.obj_type).items():
            self.fields[name] = field
            custom_fields.append(name)
        self.custom_fields = custom_fields

        # If editing an existing object, initialize values for all custom fields
        if self.instance.pk:
            existing_values = CustomFieldValue.objects.filter(obj_type=self.obj_type, obj_id=self.instance.pk)\
                .select_related('field')
            for cfv in existing_values:
                self.initial['cf_{}'.format(str(cfv.field.name))] = cfv.value

    def _save_custom_fields(self):

        for field_name in self.custom_fields:
            if self.cleaned_data[field_name] not in [None, u'']:
                try:
                    cfv = CustomFieldValue.objects.select_related('field').get(field=self.fields[field_name].model,
                                                                               obj_type=self.obj_type,
                                                                               obj_id=self.instance.pk)
                except CustomFieldValue.DoesNotExist:
                    cfv = CustomFieldValue(
                        field=self.fields[field_name].model,
                        obj_type=self.obj_type,
                        obj_id=self.instance.pk
                    )
                cfv.value = self.cleaned_data[field_name]
                cfv.save()

    def save(self, commit=True):
        obj = super(CustomFieldForm, self).save(commit)

        # Handle custom fields the same way we do M2M fields
        if commit:
            self._save_custom_fields()
        else:
            self.save_custom_fields = self._save_custom_fields

        return obj


class CustomFieldBulkEditForm(forms.Form):
    custom_fields = []

    def __init__(self, model, *args, **kwargs):

        self.obj_type = ContentType.objects.get_for_model(model)

        super(CustomFieldBulkEditForm, self).__init__(*args, **kwargs)

        # Add all applicable CustomFields to the form
        custom_fields = []
        for name, field in get_custom_fields_for_model(self.obj_type, bulk_editing=True).items():
            field.required = False
            self.fields[name] = field
            custom_fields.append(name)
        self.custom_fields = custom_fields
