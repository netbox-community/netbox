import binascii
import os

from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields import JSONField
from django.core.exceptions import FieldError, ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from utilities.permissions import resolve_permission
from utilities.utils import flatten_dict


__all__ = (
    'ObjectPermission',
    'Token',
    'UserConfig',
)


class UserConfig(models.Model):
    """
    This model stores arbitrary user-specific preferences in a JSON data structure.
    """
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        related_name='config'
    )
    data = JSONField(
        default=dict
    )

    class Meta:
        ordering = ['user']
        verbose_name = verbose_name_plural = 'User Preferences'

    def get(self, path, default=None):
        """
        Retrieve a configuration parameter specified by its dotted path. Example:

            userconfig.get('foo.bar.baz')

        :param path: Dotted path to the configuration key. For example, 'foo.bar' returns self.data['foo']['bar'].
        :param default: Default value to return for a nonexistent key (default: None).
        """
        d = self.data
        keys = path.split('.')

        # Iterate down the hierarchy, returning the default value if any invalid key is encountered
        for key in keys:
            if type(d) is dict and key in d:
                d = d.get(key)
            else:
                return default

        return d

    def all(self):
        """
        Return a dictionary of all defined keys and their values.
        """
        return flatten_dict(self.data)

    def set(self, path, value, commit=False):
        """
        Define or overwrite a configuration parameter. Example:

            userconfig.set('foo.bar.baz', 123)

        Leaf nodes (those which are not dictionaries of other nodes) cannot be overwritten as dictionaries. Similarly,
        branch nodes (dictionaries) cannot be overwritten as single values. (A TypeError exception will be raised.) In
        both cases, the existing key must first be cleared. This safeguard is in place to help avoid inadvertently
        overwriting the wrong key.

        :param path: Dotted path to the configuration key. For example, 'foo.bar' sets self.data['foo']['bar'].
        :param value: The value to be written. This can be any type supported by JSON.
        :param commit: If true, the UserConfig instance will be saved once the new value has been applied.
        """
        d = self.data
        keys = path.split('.')

        # Iterate through the hierarchy to find the key we're setting. Raise TypeError if we encounter any
        # interim leaf nodes (keys which do not contain dictionaries).
        for i, key in enumerate(keys[:-1]):
            if key in d and type(d[key]) is dict:
                d = d[key]
            elif key in d:
                err_path = '.'.join(path.split('.')[:i + 1])
                raise TypeError(f"Key '{err_path}' is a leaf node; cannot assign new keys")
            else:
                d = d.setdefault(key, {})

        # Set a key based on the last item in the path. Raise TypeError if attempting to overwrite a non-leaf node.
        key = keys[-1]
        if key in d and type(d[key]) is dict:
            raise TypeError(f"Key '{path}' has child keys; cannot assign a value")
        else:
            d[key] = value

        if commit:
            self.save()

    def clear(self, path, commit=False):
        """
        Delete a configuration parameter specified by its dotted path. The key and any child keys will be deleted.
        Example:

            userconfig.clear('foo.bar.baz')

        Invalid keys will be ignored silently.

        :param path: Dotted path to the configuration key. For example, 'foo.bar' deletes self.data['foo']['bar'].
        :param commit: If true, the UserConfig instance will be saved once the new value has been applied.
        """
        d = self.data
        keys = path.split('.')

        for key in keys[:-1]:
            if key not in d:
                break
            if type(d[key]) is dict:
                d = d[key]

        key = keys[-1]
        d.pop(key, None)  # Avoid a KeyError on invalid keys

        if commit:
            self.save()


@receiver(post_save, sender=User)
def create_userconfig(instance, created, **kwargs):
    """
    Automatically create a new UserConfig when a new User is created.
    """
    if created:
        UserConfig(user=instance).save()


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
        max_length=200,
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
        return super().save(*args, **kwargs)

    def generate_key(self):
        # Generate a random 160-bit key expressed in hexadecimal.
        return binascii.hexlify(os.urandom(20)).decode()

    @property
    def is_expired(self):
        if self.expires is None or timezone.now() < self.expires:
            return False
        return True


class ObjectPermission(models.Model):
    """
    A mapping of view, add, change, and/or delete permission for users and/or groups to an arbitrary set of objects
    identified by ORM query parameters.
    """
    users = models.ManyToManyField(
        to=User,
        blank=True,
        related_name='object_permissions'
    )
    groups = models.ManyToManyField(
        to=Group,
        blank=True,
        related_name='object_permissions'
    )
    content_types = models.ManyToManyField(
        to=ContentType,
        limit_choices_to={
            'app_label__in': [
                'circuits', 'dcim', 'extras', 'ipam', 'secrets', 'tenancy', 'virtualization',
            ],
        },
        related_name='object_permissions'
    )
    attrs = JSONField(
        blank=True,
        null=True,
        verbose_name='Attributes'
    )
    can_view = models.BooleanField(
        default=False
    )
    can_add = models.BooleanField(
        default=False
    )
    can_change = models.BooleanField(
        default=False
    )
    can_delete = models.BooleanField(
        default=False
    )

    def __str__(self):
        return "Object permission"

    def clean(self):

        # Validate the specified model attributes by attempting to execute a query. We don't care whether the query
        # returns anything; we just want to make sure the specified attributes are valid.
        if self.attrs:
            model = self.model.model_class()
            try:
                model.objects.filter(**self.attrs).exists()
            except FieldError as e:
                raise ValidationError({
                    'attrs': f'Invalid attributes for {model}: {e}'
                })
