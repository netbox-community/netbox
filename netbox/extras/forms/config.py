from django import forms

from netbox.config import get_config, PARAMS

__all__ = (
    'ConfigRevisionForm',
)


EMPTY_VALUES = ('', None, [], ())


class FormMetaclass(forms.models.ModelFormMetaclass):

    def __new__(mcs, name, bases, attrs):
        config = get_config()

        # Emulate a declared field for each supported configuration parameter
        param_fields = {}
        for param in PARAMS:
            help_text = f'{param.description}<br />' if param.description else ''
            help_text += f'Current value: <strong>{getattr(config, param.name)}</strong>'
            field_kwargs = {
                'required': False,
                'label': param.label,
                'help_text': help_text,
            }
            field_kwargs.update(**param.field_kwargs)
            param_fields[param.name] = param.field(**field_kwargs)
        attrs.update(param_fields)

        return super().__new__(mcs, name, bases, attrs)


class ConfigRevisionForm(forms.BaseModelForm, metaclass=FormMetaclass):
    """
    Form for creating a new ConfigRevision.
    """
    class Meta:
        widgets = {
            'comment': forms.Textarea(),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Populate JSON data on the instance
        instance.data = self.render_json()

        if commit:
            instance.save()

        return instance

    def render_json(self):
        json = {}

        # Iterate through each field and populate non-empty values
        for field_name in self.declared_fields:
            if field_name in self.cleaned_data and self.cleaned_data[field_name] not in EMPTY_VALUES:
                json[field_name] = self.cleaned_data[field_name]

        return json
