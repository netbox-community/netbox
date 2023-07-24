from django import forms
from django.utils.translation import gettext as _

from users.models import Token

__all__ = (
    'TokenAdminForm',
)


class TokenAdminForm(forms.ModelForm):
    key = forms.CharField(
        required=False,
        help_text=_("If no key is provided, one will be generated automatically.")
    )

    class Meta:
        fields = [
            'user', 'key', 'write_enabled', 'expires', 'description', 'allowed_ips'
        ]
        model = Token
