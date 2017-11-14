from __future__ import unicode_literals

from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm as DjangoPasswordChangeForm

from utilities.forms import BootstrapMixin
from .models import Token


class LoginForm(BootstrapMixin, AuthenticationForm):

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs['placeholder'] = ''
        self.fields['password'].widget.attrs['placeholder'] = ''


class PasswordChangeForm(BootstrapMixin, DjangoPasswordChangeForm):
    pass


class TokenForm(BootstrapMixin, forms.ModelForm):
    key = forms.CharField(required=False, help_text="If no key is provided, one will be generated automatically.")

    class Meta:
        model = Token
        fields = ['key', 'write_enabled', 'expires', 'description']
        help_texts = {
            'expires': 'YYYY-MM-DD [HH:MM:SS]'
        }
