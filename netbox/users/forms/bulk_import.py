from django import forms
from django.utils.translation import gettext as _
from users.models import *
from users.choices import TokenVersionChoices
from utilities.forms import CSVModelForm


__all__ = (
    'GroupImportForm',
    'UserImportForm',
    'TokenImportForm',
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
        fields = ('user', 'version', 'token', 'write_enabled', 'expires', 'description',)
