from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
)

from utilities.forms import BootstrapMixin

__all__ = (
    'LoginForm',
    'PasswordChangeForm',
)


class LoginForm(BootstrapMixin, AuthenticationForm):
    """
    Used to authenticate a user by username and password.
    """
    pass


class PasswordChangeForm(BootstrapMixin, DjangoPasswordChangeForm):
    """
    This form enables a user to change his or her own password.
    """
    pass
