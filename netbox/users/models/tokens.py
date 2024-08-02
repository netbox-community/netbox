import binascii
import os

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from netaddr import IPNetwork

from ipam.fields import IPNetworkField
from utilities.querysets import RestrictedQuerySet

__all__ = (
    'Token',
)


class Token(models.Model):
    """
    An API token used for user authentication. This extends the stock model to allow each user to have multiple tokens.
    It also supports setting an expiration time and toggling write ability.
    """
    user = models.ForeignKey(
        to='users.User',
        on_delete=models.CASCADE,
        related_name='tokens'
    )
    created = models.DateTimeField(
        verbose_name=_('created'),
        auto_now_add=True
    )
    expires = models.DateTimeField(
        verbose_name=_('expires'),
        blank=True,
        null=True
    )
    last_used = models.DateTimeField(
        verbose_name=_('last used'),
        blank=True,
        null=True
    )
    key = models.CharField(
        verbose_name=_('key'),
        max_length=40,
        unique=True,
        validators=[MinLengthValidator(40)]
    )
    write_enabled = models.BooleanField(
        verbose_name=_('write enabled'),
        default=True,
        help_text=_('Permit create/update/delete operations using this key')
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    allowed_ips = ArrayField(
        base_field=IPNetworkField(),
        blank=True,
        null=True,
        verbose_name=_('allowed IPs'),
        help_text=_(
            'Allowed IPv4/IPv6 networks from where the token can be used. Leave blank for no restrictions. '
            'Ex: "10.1.1.0/24, 192.168.10.16/32, 2001:DB8:1::/64"'
        ),
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        verbose_name = _('token')
        verbose_name_plural = _('tokens')

    def __str__(self):
        return self.key if settings.ALLOW_TOKEN_RETRIEVAL else self.partial

    def get_absolute_url(self):
        return reverse('users:token', args=[self.pk])

    @property
    def partial(self):
        return f'**********************************{self.key[-6:]}' if self.key else ''

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super().save(*args, **kwargs)

    @staticmethod
    def generate_key():
        # Generate a random 160-bit key expressed in hexadecimal.
        return binascii.hexlify(os.urandom(20)).decode()

    @property
    def is_expired(self):
        if self.expires is None or timezone.now() < self.expires:
            return False
        return True

    def validate_client_ip(self, client_ip):
        """
        Validate the API client IP address against the source IP restrictions (if any) set on the token.
        """
        if not self.allowed_ips:
            return True

        for ip_network in self.allowed_ips:
            if client_ip in IPNetwork(ip_network):
                return True

        return False
