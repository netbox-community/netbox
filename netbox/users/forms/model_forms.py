from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.contrib.postgres.forms import SimpleArrayField
from django.core.exceptions import FieldError
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from core.models import ObjectType
from ipam.formfields import IPNetworkFormField
from ipam.validators import prefix_validator
from netbox.preferences import PREFERENCES
from users.constants import *
from users.models import *
from utilities.data import flatten_dict
from utilities.forms.fields import ContentTypeMultipleChoiceField, DynamicModelMultipleChoiceField
from utilities.forms.rendering import FieldSet
from utilities.forms.widgets import DateTimePicker
from utilities.permissions import qs_filter_from_constraints

__all__ = (
    'GroupForm',
    'ObjectPermissionForm',
    'TokenForm',
    'UserConfigForm',
    'UserForm',
    'UserTokenForm',
    'TokenForm',
)


class UserConfigFormMetaclass(forms.models.ModelFormMetaclass):

    def __new__(mcs, name, bases, attrs):

        # Emulate a declared field for each supported user preference
        preference_fields = {}
        for field_name, preference in PREFERENCES.items():
            description = f'{preference.description}<br />' if preference.description else ''
            help_text = f'<code>{field_name}</code>'
            if preference.description:
                help_text = f'{preference.description}<br />{help_text}'
            if warning := preference.warning:
                help_text = f'<span class="text-danger"><i class="mdi mdi-alert"></i> {warning}</span><br />{help_text}'
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


class UserConfigForm(forms.ModelForm, metaclass=UserConfigFormMetaclass):
    fieldsets = (
        FieldSet(
            'locale.language', 'pagination.per_page', 'pagination.placement', 'ui.htmx_navigation',
            name=_('User Interface')
        ),
        FieldSet('data_format', name=_('Miscellaneous')),
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


class UserTokenForm(forms.ModelForm):
    key = forms.CharField(
        label=_('Key'),
        help_text=_(
            'Keys must be at least 40 characters in length. <strong>Be sure to record your key</strong> prior to '
            'submitting this form, as it may no longer be accessible once the token has been created.'
        ),
        widget=forms.TextInput(
            attrs={'data-clipboard': 'true'}
        )
    )
    allowed_ips = SimpleArrayField(
        base_field=IPNetworkFormField(validators=[prefix_validator]),
        required=False,
        label=_('Allowed IPs'),
        help_text=_(
            'Allowed IPv4/IPv6 networks from where the token can be used. Leave blank for no restrictions. '
            'Example: <code>10.1.1.0/24,192.168.10.16/32,2001:db8:1::/64</code>'
        ),
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

        # Generate an initial random key if none has been specified
        if not self.instance.pk and not self.initial.get('key'):
            self.initial['key'] = Token.generate_key()


class TokenForm(UserTokenForm):
    user = forms.ModelChoiceField(
        queryset=get_user_model().objects.order_by('username'),
        label=_('User')
    )

    class Meta:
        model = Token
        fields = [
            'user', 'key', 'write_enabled', 'expires', 'description', 'allowed_ips',
        ]
        widgets = {
            'expires': DateTimePicker(),
        }


class UserForm(forms.ModelForm):
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(),
        required=True,
    )
    confirm_password = forms.CharField(
        label=_('Confirm password'),
        widget=forms.PasswordInput(),
        required=True,
        help_text=_("Enter the same password as before, for verification."),
    )
    groups = DynamicModelMultipleChoiceField(
        label=_('Groups'),
        required=False,
        queryset=Group.objects.all()
    )
    object_permissions = DynamicModelMultipleChoiceField(
        required=False,
        label=_('Permissions'),
        queryset=ObjectPermission.objects.all()
    )

    fieldsets = (
        FieldSet('username', 'password', 'confirm_password', 'first_name', 'last_name', 'email', name=_('User')),
        FieldSet('groups', name=_('Groups')),
        FieldSet('is_active', 'is_staff', 'is_superuser', name=_('Status')),
        FieldSet('object_permissions', name=_('Permissions')),
    )

    class Meta:
        model = User
        fields = [
            'username', 'first_name', 'last_name', 'email', 'groups', 'object_permissions',
            'is_active', 'is_staff', 'is_superuser',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            # Password fields are optional for existing Users
            self.fields['password'].required = False
            self.fields['confirm_password'].required = False

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # On edit, check if we have to save the password
        if self.cleaned_data.get('password'):
            instance.set_password(self.cleaned_data.get('password'))
            instance.save()

        return instance

    def clean(self):

        # Check that password confirmation matches if password is set
        if self.cleaned_data['password'] and self.cleaned_data['password'] != self.cleaned_data['confirm_password']:
            raise forms.ValidationError(_("Passwords do not match! Please check your input and try again."))

        # Enforce password validation rules (if configured)
        if self.cleaned_data['password']:
            password_validation.validate_password(self.cleaned_data['password'], self.instance)


class GroupForm(forms.ModelForm):
    users = DynamicModelMultipleChoiceField(
        label=_('Users'),
        required=False,
        queryset=get_user_model().objects.all()
    )
    object_permissions = DynamicModelMultipleChoiceField(
        required=False,
        label=_('Permissions'),
        queryset=ObjectPermission.objects.all()
    )

    fieldsets = (
        FieldSet('name', 'description'),
        FieldSet('users', name=_('Users')),
        FieldSet('object_permissions', name=_('Permissions')),
    )

    class Meta:
        model = Group
        fields = [
            'name', 'description', 'users', 'object_permissions',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Populate assigned users and permissions
        if self.instance.pk:
            self.fields['users'].initial = self.instance.users.values_list('id', flat=True)

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # Update assigned users
        instance.users.set(self.cleaned_data['users'])

        return instance


class ObjectPermissionForm(forms.ModelForm):
    object_types = ContentTypeMultipleChoiceField(
        label=_('Object types'),
        queryset=ObjectType.objects.all(),
        limit_choices_to=OBJECTPERMISSION_OBJECT_TYPES,
        widget=forms.SelectMultiple(attrs={'size': 6})
    )
    can_view = forms.BooleanField(
        required=False
    )
    can_add = forms.BooleanField(
        required=False
    )
    can_change = forms.BooleanField(
        required=False
    )
    can_delete = forms.BooleanField(
        required=False
    )
    actions = SimpleArrayField(
        label=_('Additional actions'),
        base_field=forms.CharField(),
        required=False,
        help_text=_('Actions granted in addition to those listed above')
    )
    users = DynamicModelMultipleChoiceField(
        label=_('Users'),
        required=False,
        queryset=get_user_model().objects.all()
    )
    groups = DynamicModelMultipleChoiceField(
        label=_('Groups'),
        required=False,
        queryset=Group.objects.all()
    )

    fieldsets = (
        FieldSet('name', 'description', 'enabled'),
        FieldSet('can_view', 'can_add', 'can_change', 'can_delete', 'actions', name=_('Actions')),
        FieldSet('object_types', name=_('Objects')),
        FieldSet('groups', 'users', name=_('Assignment')),
        FieldSet('constraints', name=_('Constraints'))
    )

    class Meta:
        model = ObjectPermission
        fields = [
            'name', 'description', 'enabled', 'object_types', 'users', 'groups', 'constraints', 'actions',
        ]
        help_texts = {
            'constraints': _(
                'JSON expression of a queryset filter that will return only permitted objects. Leave null '
                'to match all objects of this type. A list of multiple objects will result in a logical OR '
                'operation.'
            )
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the actions field optional since the form uses it only for non-CRUD actions
        self.fields['actions'].required = False

        # Populate assigned users and groups
        if self.instance.pk:
            self.fields['groups'].initial = self.instance.groups.values_list('id', flat=True)
            self.fields['users'].initial = self.instance.users.values_list('id', flat=True)

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
            raise forms.ValidationError(_("At least one action must be selected."))

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
                except (FieldError, ValueError) as e:
                    raise forms.ValidationError({
                        'constraints': _('Invalid filter for {model}: {error}').format(model=model, error=e)
                    })

    def save(self, *args, **kwargs):
        instance = super().save(*args, **kwargs)

        # Update assigned users and groups
        instance.users.set(self.cleaned_data['users'])
        instance.groups.set(self.cleaned_data['groups'])

        return instance
