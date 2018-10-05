from __future__ import unicode_literals

import binascii
import os

from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Token(models.Model):
    """
    An API token used for user authentication. This extends the stock model to allow each user to have multiple tokens.
    It also supports setting an expiration time and toggling write ability.
    """
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='tokens'
    )
    created = models.DateTimeField(
        auto_now_add=True
    )
    expires = models.DateTimeField(
        blank=True,
        null=True
    )
    key = models.CharField(
        max_length=40,
        unique=True,
        validators=[MinLengthValidator(40)]
    )
    write_enabled = models.BooleanField(
        default=True,
        help_text='Permit create/update/delete operations using this key'
    )
    description = models.CharField(
        max_length=100,
        blank=True
    )

    class Meta:
        pass

    def __str__(self):
        # Only display the last 24 bits of the token to avoid accidental exposure.
        return "{} ({})".format(self.key[-6:], self.user)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        # Generate a random 160-bit key expressed in hexadecimal.
        return binascii.hexlify(os.urandom(20)).decode()

    @property
    def is_expired(self):
        if self.expires is None or timezone.now() < self.expires:
            return False
        return True
