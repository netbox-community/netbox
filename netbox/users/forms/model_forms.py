from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.models import Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.forms import SimpleArrayField
from django.utils.html import mark_safe
from django.utils.translation import gettext as _

from ipam.formfields import IPNetworkFormField
from ipam.validators import prefix_validator
from netbox.preferences import PREFERENCES
from utilities.forms import BootstrapMixin
from utilities.forms.fields import ContentTypeMultipleChoiceField, DynamicModelChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.widgets import DateTimePicker
from utilities.utils import flatten_dict
from users.constants import *
from users.models import *


__all__ = (
    'GroupForm',
    'LoginForm',
    'ObjectPermissionForm',
    'PasswordChangeForm',
    'TokenForm',
    'UserConfigForm',
    'UserForm',
)


class LoginForm(BootstrapMixin, AuthenticationForm):
    pass


class PasswordChangeForm(BootstrapMixin, DjangoPasswordChangeForm):
    pass


class UserConfigFormMetaclass(forms.models.ModelFormMetaclass):

    def __new__(mcs, name, bases, attrs):

        # Emulate a declared field for each supported user preference
        preference_fields = {}
        for field_name, preference in PREFERENCES.items():
            description = f'{preference.description}<br />' if preference.description else ''
            help_text = f'{description}<code>{field_name}</code>'
            field_kwargs = {
                'label': preference.label,
                'choices': preference.choices,
                'help_text': mark_safe(help_text),
                'coerce': preference.coerce,
                'required': False,
                'widget': forms.Select,
            }
            preference_fields[field_name] = forms.TypedChoiceField(**field_kwargs)
        attrs.update(preference_fields)

        return super().__new__(mcs, name, bases, attrs)


class UserConfigForm(BootstrapMixin, forms.ModelForm, metaclass=UserConfigFormMetaclass):
    fieldsets = (
        ('User Interface', (
            'pagination.per_page',
            'pagination.placement',
            'ui.colormode',
        )),
        ('Miscellaneous', (
            'data_format',
        )),
    )
    # List of clearable preferences
    pk = forms.MultipleChoiceField(
        choices=[],
        required=False
    )

    class Meta:
        model = UserConfig
        fields = ()

    def __init__(self, *args, instance=None, **kwargs):

        # Get initial data from UserConfig instance
        initial_data = flatten_dict(instance.data)
        kwargs['initial'] = initial_data

        super().__init__(*args, instance=instance, **kwargs)

        # Compile clearable preference choices
        self.fields['pk'].choices = (
            (f'tables.{table_name}', '') for table_name in instance.data.get('tables', [])
        )

    def save(self, *args, **kwargs):

        # Set UserConfig data
        for pref_name, value in self.cleaned_data.items():
            if pref_name == 'pk':
                continue
            self.instance.set(pref_name, value, commit=False)

        # Clear selected preferences
        for preference in self.cleaned_data['pk']:
            self.instance.clear(preference)

        return super().save(*args, **kwargs)

    @property
    def plugin_fields(self):
        return [
            name for name in self.fields.keys() if name.startswith('plugins.')
        ]


class TokenForm(BootstrapMixin, forms.ModelForm):
    key = forms.CharField(
        required=False,
        help_text=_("If no key is provided, one will be generated automatically.")
    )
    allowed_ips = SimpleArrayField(
        base_field=IPNetworkFormField(validators=[prefix_validator]),
        required=False,
        label=_('Allowed IPs'),
        help_text=_('Allowed IPv4/IPv6 networks from where the token can be used. Leave blank for no restrictions. '
                    'Example: <code>10.1.1.0/24,192.168.10.16/32,2001:db8:1::/64</code>'),
    )

    class Meta:
        model = Token
        fields = [
            'key', 'write_enabled', 'expires', 'description', 'allowed_ips',
        ]
        widgets = {
            'expires': DateTimePicker(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Omit the key field if token retrieval is not permitted
        if self.instance.pk and not settings.ALLOW_TOKEN_RETRIEVAL:
            del self.fields['key']


class UserForm(BootstrapMixin, forms.ModelForm):
    groups = DynamicModelMultipleChoiceField(
        required=False,
        queryset=Group.objects.all()
    )
    object_permissions = DynamicModelMultipleChoiceField(
        required=False,
        label=_('Permissions'),
        queryset=ObjectPermission.objects.all()
    )

    fieldsets = (
        ('User', ('username', 'first_name', 'last_name', 'email', )),
        ('Groups', ('groups', )),
        ('Status', ('is_active', 'is_staff', 'is_superuser', )),
        ('Important Dates', ('last_login', 'date_joined', )),
        ('Permissions', ('object_permissions', )),
    )

    class Meta:
        model = NetBoxUser
        fields = [
            'username', 'first_name', 'last_name', 'email', 'groups', 'object_permissions',
            'is_active', 'is_staff', 'is_superuser', 'last_login', 'date_joined',
        ]


class GroupForm(BootstrapMixin, forms.ModelForm):
    users = DynamicModelMultipleChoiceField(
        required=False,
        queryset=get_user_model().objects.all()
    )
    object_permissions = DynamicModelMultipleChoiceField(
        required=False,
        label=_('Permissions'),
        queryset=ObjectPermission.objects.all()
    )

    fieldsets = (
        (None, ('name', )),
        ('Users', ('users', )),
        ('Permissions', ('object_permissions', )),
    )

    class Meta:
        model = NetBoxGroup
        fields = [
            'name', 'users', 'object_permissions',
        ]


class ObjectPermissionForm(BootstrapMixin, forms.ModelForm):
    users = DynamicModelMultipleChoiceField(
        required=False,
        queryset=get_user_model().objects.all()
    )
    groups = DynamicModelMultipleChoiceField(
        required=False,
        queryset=Group.objects.all()
    )
    object_types = ContentTypeMultipleChoiceField(
        queryset=ContentType.objects.all(),
        limit_choices_to=OBJECTPERMISSION_OBJECT_TYPES
    )

    can_view = forms.BooleanField(required=False)
    can_add = forms.BooleanField(required=False)
    can_change = forms.BooleanField(required=False)
    can_delete = forms.BooleanField(required=False)

    fieldsets = (
        (None, ('name', 'description', 'enabled',)),
        ('Actions', ('can_view', 'can_add', 'can_change', 'can_delete', 'actions')),
        ('Objects', ('object_types')),
        ('Assignment', ('groups', 'users')),
        ('Constraints', ('constraints',))
    )

    class Meta:
        model = ObjectPermission
        fields = [
            'name', 'description', 'enabled', 'object_types', 'users', 'groups', 'constraints', 'actions',
        ]

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
                    tokens = {
                        CONSTRAINT_TOKEN_USER: 0,  # Replace token with a null user ID
                    }
                    model.objects.filter(qs_filter_from_constraints(constraints, tokens)).exists()
                except FieldError as e:
                    raise ValidationError({
                        'constraints': f'Invalid filter for {model}: {e}'
                    })
