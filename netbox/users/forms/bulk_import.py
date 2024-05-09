from django import forms
from django.utils.translation import gettext as _
from users.models import *
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
            'username', 'first_name', 'last_name', 'email', 'password', 'is_staff',
            'is_active', 'is_superuser'
        )

    def save(self, *args, **kwargs):
        # Set the hashed password
        self.instance.set_password(self.cleaned_data.get('password'))

        return super().save(*args, **kwargs)


class TokenImportForm(CSVModelForm):
    key = forms.CharField(
        label=_('Key'),
        required=False,
        help_text=_("If no key is provided, one will be generated automatically.")
    )

    class Meta:
        model = Token
        fields = ('user', 'key', 'write_enabled', 'expires', 'description',)
