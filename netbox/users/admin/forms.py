from django import forms
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import FieldError, ValidationError
from django.db.models import Q

from users.constants import OBJECTPERMISSION_OBJECT_TYPES
from users.models import ObjectPermission, Token
from utilities.forms.fields import ContentTypeMultipleChoiceField

__all__ = (
    'ObjectPermissionForm',
    'TokenAdminForm',
)


class TokenAdminForm(forms.ModelForm):
    key = forms.CharField(
        required=False,
        help_text="If no key is provided, one will be generated automatically."
    )

    class Meta:
        fields = [
            'user', 'key', 'write_enabled', 'expires', 'description'
        ]
        model = Token


class ObjectPermissionForm(forms.ModelForm):
    object_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=OBJECTPERMISSION_OBJECT_TYPES
    )
    can_view = forms.BooleanField(required=False)
    can_add = forms.BooleanField(required=False)
    can_change = forms.BooleanField(required=False)
    can_delete = forms.BooleanField(required=False)

    class Meta:
        model = ObjectPermission
        exclude = []
        help_texts = {
            'actions': 'Actions granted in addition to those listed above',
            'constraints': 'JSON expression of a queryset filter that will return only permitted objects. Leave null '
                           'to match all objects of this type. A list of multiple objects will result in a logical OR '
                           'operation.'
        }
        labels = {
            'actions': 'Additional actions'
        }
        widgets = {
            'constraints': forms.Textarea(attrs={'class': 'vLargeTextField'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the actions field optional since the admin form uses it only for non-CRUD actions
        self.fields['actions'].required = False

        # Order group and user fields
        self.fields['groups'].queryset = self.fields['groups'].queryset.order_by('name')
        self.fields['users'].queryset = self.fields['users'].queryset.order_by('username')

        # Check the appropriate checkboxes when editing an existing ObjectPermission
        if self.instance.pk:
            for action in ['view', 'add', 'change', 'delete']:
                if action in self.instance.actions:
                    self.fields[f'can_{action}'].initial = True
                    self.instance.actions.remove(action)

    def clean(self):
        super().clean()

        object_types = self.cleaned_data.get('object_types')
        constraints = self.cleaned_data.get('constraints')

        # Append any of the selected CRUD checkboxes to the actions list
        if not self.cleaned_data.get('actions'):
            self.cleaned_data['actions'] = list()
        for action in ['view', 'add', 'change', 'delete']:
            if self.cleaned_data[f'can_{action}'] and action not in self.cleaned_data['actions']:
                self.cleaned_data['actions'].append(action)

        # At least one action must be specified
        if not self.cleaned_data['actions']:
            raise ValidationError("At least one action must be selected.")

        # Validate the specified model constraints by attempting to execute a query. We don't care whether the query
        # returns anything; we just want to make sure the specified constraints are valid.
        if object_types and constraints:
            # Normalize the constraints to a list of dicts
            if type(constraints) is not list:
                constraints = [constraints]
            for ct in object_types:
                model = ct.model_class()
                try:
                    model.objects.filter(*[Q(**c) for c in constraints]).exists()
                except FieldError as e:
                    raise ValidationError({
                        'constraints': f'Invalid filter for {model}: {e}'
                    })
