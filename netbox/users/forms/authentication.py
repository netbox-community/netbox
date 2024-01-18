from django.contrib.auth.forms import (
    AuthenticationForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
)

__all__ = (
    'LoginForm',
    'PasswordChangeForm',
)


class LoginForm(AuthenticationForm):
    """
    Used to authenticate a user by username and password.
    """
    pass


class PasswordChangeForm(DjangoPasswordChangeForm):
    """
    This form enables a user to change his or her own password.
    """
    pass
