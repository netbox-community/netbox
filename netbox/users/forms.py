from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.postgres.forms import SimpleArrayField

from utilities.forms import BootstrapMixin, DateTimePicker
from .models import Token
from ipam.formfields import IPNetworkFormField


class LoginForm(BootstrapMixin, AuthenticationForm):
    pass


class PasswordChangeForm(BootstrapMixin, DjangoPasswordChangeForm):
    pass


class TokenForm(BootstrapMixin, forms.ModelForm):
    key = forms.CharField(
        required=False,
        help_text="If no key is provided, one will be generated automatically."
    )
    allowed_ips = SimpleArrayField(
        base_field=IPNetworkFormField(),
        required=False,
        help_text='Allowed IPv4/IPv6 networks from where the token can be used. Leave blank for no restrictions. Ex: "10.1.1.0/24, 192.168.10.16/32, 2001:DB8:1::/64"',
    )

    class Meta:
        model = Token
        fields = [
            'key', 'write_enabled', 'expires', 'description', 'allowed_ips',
        ]
        widgets = {
            'expires': DateTimePicker(),
        }
