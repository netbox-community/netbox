from django import forms
from django.contrib.contenttypes.models import ContentType

from .models import CF_TYPE_BOOLEAN, CF_TYPE_DATE, CF_TYPE_INTEGER, CF_TYPE_SELECT, CustomField, CustomFieldValue


class CustomFieldForm(forms.ModelForm):
    custom_fields = []

    def __init__(self, *args, **kwargs):

        super(CustomFieldForm, self).__init__(*args, **kwargs)

        obj_type = ContentType.objects.get_for_model(self._meta.model)

        # Find all CustomFields for this model
        custom_fields = CustomField.objects.filter(obj_type=obj_type)
        for cf in custom_fields:

            field_name = 'cf_{}'.format(str(cf.name))

            # Integer
            if cf.type == CF_TYPE_INTEGER:
                field = forms.IntegerField(required=cf.required, initial=cf.default)

            # Boolean
            elif cf.type == CF_TYPE_BOOLEAN:
                if cf.required:
                    field = forms.BooleanField(required=False, initial=bool(cf.default))
                else:
                    field = forms.NullBooleanField(required=False, initial=bool(cf.default))

            # Date
            elif cf.type == CF_TYPE_DATE:
                field = forms.DateField(required=cf.required, initial=cf.default)

            # Select
            elif cf.type == CF_TYPE_SELECT:
                field = forms.ModelChoiceField(queryset=cf.choices.all(), required=cf.required)

            # Text
            else:
                field = forms.CharField(max_length=100, required=cf.required, initial=cf.default)

            field.model = cf
            field.label = cf.label if cf.label else cf.name
            field.help_text = cf.description
            self.fields[field_name] = field
            self.custom_fields.append(field_name)

        # If editing an existing object, initialize values for all custom fields
        if self.instance.pk:
            existing_values = CustomFieldValue.objects.filter(obj_type=obj_type, obj_id=self.instance.pk)\
                .select_related('field')
            for cfv in existing_values:
                self.initial['cf_{}'.format(str(cfv.field.name))] = cfv.value

    def _save_custom_fields(self):

        if self.instance.pk:
            obj_type = ContentType.objects.get_for_model(self.instance)

            for field_name in self.custom_fields:

                try:
                    cfv = CustomFieldValue.objects.get(field=self.fields[field_name].model, obj_type=obj_type,
                                                       obj_id=self.instance.pk)
                except CustomFieldValue.DoesNotExist:
                    cfv = CustomFieldValue(
                        field=self.fields[field_name].model,
                        obj_type=obj_type,
                        obj_id=self.instance.pk
                    )
                if cfv.pk and self.cleaned_data[field_name] is None:
                    cfv.delete()
                elif self.cleaned_data[field_name] is not None:
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
