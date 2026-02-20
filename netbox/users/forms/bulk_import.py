from django import forms
from django.utils.translation import gettext as _

from users.choices import TokenVersionChoices
from users.models import *
from utilities.forms import CSVModelForm
from utilities.forms.fields import CSVModelChoiceField, CSVModelMultipleChoiceField

__all__ = (
    'GroupImportForm',
    'OwnerGroupImportForm',
    'OwnerImportForm',
    'TokenImportForm',
    'UserImportForm',
)


class GroupImportForm(CSVModelForm):

    class Meta:
        model = Group
        fields = ('name', 'description')


class UserImportForm(CSVModelForm):

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'password', 'is_active', 'is_superuser'
        )

    def save(self, *args, **kwargs):
        # Set the hashed password
        self.instance.set_password(self.cleaned_data.get('password'))

        return super().save(*args, **kwargs)


class TokenImportForm(CSVModelForm):
    version = forms.ChoiceField(
        choices=TokenVersionChoices,
        initial=TokenVersionChoices.V2,
        required=False,
        help_text=_("Specify version 1 or 2 (v2 will be used by default)")
    )
    token = forms.CharField(
        label=_('Token'),
        required=False,
        help_text=_("If no token is provided, one will be generated automatically.")
    )

    class Meta:
        model = Token
        fields = ('user', 'version', 'token', 'enabled', 'write_enabled', 'expires', 'description',)


class OwnerGroupImportForm(CSVModelForm):

    class Meta:
        model = OwnerGroup
        fields = (
            'name', 'description',
        )


class OwnerImportForm(CSVModelForm):
    group = CSVModelChoiceField(
        queryset=OwnerGroup.objects.all(),
        required=False,
        to_field_name='name',
    )
    user_groups = CSVModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        to_field_name='name',
    )
    users = CSVModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        to_field_name='username',
    )

    class Meta:
        model = Owner
        fields = (
            'group', 'name', 'description', 'user_groups', 'users',
        )
