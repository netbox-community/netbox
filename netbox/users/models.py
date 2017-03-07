import binascii
import os

from django.contrib.auth.models import User
from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Token(models.Model):
    """
    An API token used for user authentication. This extends the stock model to allow each user to have multiple tokens.
    It also supports setting an expiration time and toggling write ability.
    """
    user = models.ForeignKey(User, related_name='tokens', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField(blank=True, null=True)
    key = models.CharField(max_length=64, unique=True)
    write_enabled = models.BooleanField(default=True, help_text="Permit create/update/delete operations using this key")
    description = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return u"API key for {}".format(self.user)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(Token, self).save(*args, **kwargs)

    def generate_key(self):
        # Generate a random 256-bit key expressed in hexadecimal.
        return binascii.hexlify(os.urandom(32)).decode()
