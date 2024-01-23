from django.urls import reverse

from users.models import Token


class UserToken(Token):
    """
    Proxy model for users to manage their own API tokens.
    """
    _netbox_private = True

    class Meta:
        proxy = True
        verbose_name = 'token'

    def get_absolute_url(self):
        return reverse('account:usertoken', args=[self.pk])
