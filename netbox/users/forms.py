from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm as DjangoPasswordChangeForm

from utilities.forms import BootstrapMixin, DateTimePicker
from utilities.paginator import EnhancedPaginator
from utilities.utils import flatten_dict
from .models import Token, UserConfig


class LoginForm(BootstrapMixin, AuthenticationForm):
    pass


class PasswordChangeForm(BootstrapMixin, DjangoPasswordChangeForm):
    pass


def get_page_lengths():
    return [
        (v, str(v)) for v in EnhancedPaginator.default_page_lengths
    ]


class UserConfigForm(BootstrapMixin, forms.ModelForm):
    pagination__per_page = forms.TypedChoiceField(
        label='Page length',
        coerce=lambda val: int(val),
        choices=get_page_lengths,
        required=False
    )
    ui__colormode = forms.ChoiceField(
        label='Color mode',
        choices=(
            ('light', 'Light'),
            ('dark', 'Dark'),
        ),
        required=False
    )
    extras__configcontext__format = forms.ChoiceField(
        label='ConfigContext format',
        choices=(
            ('json', 'JSON'),
            ('yaml', 'YAML'),
        ),
        required=False
    )

    class Meta:
        model = UserConfig
        fields = ()
        fieldsets = (
            ('User Interface', (
                'pagination__per_page',
                'ui__colormode',
            )),
            ('Miscellaneous', (
                'extras__configcontext__format',
            )),
        )

    def __init__(self, *args, instance=None, **kwargs):

        # Get initial data from UserConfig instance
        initial_data = flatten_dict(instance.data, separator='__')
        kwargs['initial'] = initial_data

        super().__init__(*args, instance=instance, **kwargs)

    def save(self, *args, **kwargs):

        # Set UserConfig data
        for field_name, value in self.cleaned_data.items():
            pref_name = field_name.replace('__', '.')
            print(f'{pref_name}: {value}')
            self.instance.set(pref_name, value, commit=False)

        return super().save(*args, **kwargs)


class TokenForm(BootstrapMixin, forms.ModelForm):
    key = forms.CharField(
        required=False,
        help_text="If no key is provided, one will be generated automatically."
    )

    class Meta:
        model = Token
        fields = [
            'key', 'write_enabled', 'expires', 'description',
        ]
        widgets = {
            'expires': DateTimePicker(),
        }
