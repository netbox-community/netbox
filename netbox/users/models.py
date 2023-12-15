import binascii
import os

from django.conf import settings
from django.contrib.auth.models import Group, GroupManager, User, UserManager
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from netaddr import IPNetwork

from core.models import ContentType
from ipam.fields import IPNetworkField
from netbox.config import get_config
from utilities.querysets import RestrictedQuerySet
from utilities.utils import flatten_dict
from .constants import *

__all__ = (
    'NetBoxGroup',
    'NetBoxUser',
    'ObjectPermission',
    'Token',
    'UserConfig',
)


#
# Proxies for Django's User and Group models
#

class NetBoxUserManager(UserManager.from_queryset(RestrictedQuerySet)):
    pass


class NetBoxGroupManager(GroupManager.from_queryset(RestrictedQuerySet)):
    pass


class NetBoxUser(User):
    """
    Proxy contrib.auth.models.User for the UI
    """
    objects = NetBoxUserManager()

    class Meta:
        proxy = True
        ordering = ('username',)
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_absolute_url(self):
        return reverse('users:netboxuser', args=[self.pk])

    def clean(self):
        super().clean()

        # Check for any existing Users with names that differ only in case
        model = self._meta.model
        if model.objects.exclude(pk=self.pk).filter(username__iexact=self.username).exists():
            raise ValidationError(_("A user with this username already exists."))


class NetBoxGroup(Group):
    """
    Proxy contrib.auth.models.User for the UI
    """
    objects = NetBoxGroupManager()

    class Meta:
        proxy = True
        ordering = ('name',)
        verbose_name = _('group')
        verbose_name_plural = _('groups')

    def get_absolute_url(self):
        return reverse('users:netboxgroup', args=[self.pk])


#
# User preferences
#

class UserConfig(models.Model):
    """
    This model stores arbitrary user-specific preferences in a JSON data structure.
    """
    user = models.OneToOneField(
        to=User,
        on_delete=models.CASCADE,
        related_name='config'
    )
    data = models.JSONField(
        default=dict
    )

    _netbox_private = True

    class Meta:
        ordering = ['user']
        verbose_name = _('user preferences')
        verbose_name_plural = _('user preferences')

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
        try:
            for key in keys:
                d = d[key]
            return d
        except (TypeError, KeyError):
            pass

        # If the key is not found in the user's config, check for an application-wide default
        config = get_config()
        d = config.DEFAULT_USER_PREFERENCES
        try:
            for key in keys:
                d = d[key]
            return d
        except (TypeError, KeyError):
            pass

        # Finally, return the specified default value (if any)
        return default

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
                raise TypeError(
                    _("Key '{path}' is a leaf node; cannot assign new keys").format(path=err_path)
                )
            else:
                d = d.setdefault(key, {})

        # Set a key based on the last item in the path. Raise TypeError if attempting to overwrite a non-leaf node.
        key = keys[-1]
        if key in d and type(d[key]) is dict:
            if type(value) is dict:
                d[key].update(value)
            else:
                raise TypeError(
                    _("Key '{path}' is a dictionary; cannot assign a non-dictionary value").format(path=path)
                )
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
@receiver(post_save, sender=NetBoxUser)
def create_userconfig(instance, created, raw=False, **kwargs):
    """
    Automatically create a new UserConfig when a new User is created. Skip this if importing a user from a fixture.
    """
    if created and not raw:
        config = get_config()
        UserConfig(user=instance, data=config.DEFAULT_USER_PREFERENCES).save()


#
# REST API
#

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


#
# Permissions
#

class ObjectPermission(models.Model):
    """
    A mapping of view, add, change, and/or delete permission for users and/or groups to an arbitrary set of objects
    identified by ORM query parameters.
    """
    name = models.CharField(
        verbose_name=_('name'),
        max_length=100
    )
    description = models.CharField(
        verbose_name=_('description'),
        max_length=200,
        blank=True
    )
    enabled = models.BooleanField(
        verbose_name=_('enabled'),
        default=True
    )
    object_types = models.ManyToManyField(
        to='contenttypes.ContentType',
        limit_choices_to=OBJECTPERMISSION_OBJECT_TYPES,
        related_name='object_permissions'
    )
    groups = models.ManyToManyField(
        to=Group,
        blank=True,
        related_name='object_permissions'
    )
    users = models.ManyToManyField(
        to=User,
        blank=True,
        related_name='object_permissions'
    )
    actions = ArrayField(
        base_field=models.CharField(max_length=30),
        help_text=_("The list of actions granted by this permission")
    )
    constraints = models.JSONField(
        blank=True,
        null=True,
        verbose_name=_('constraints'),
        help_text=_("Queryset filter matching the applicable objects of the selected type(s)")
    )

    objects = RestrictedQuerySet.as_manager()

    class Meta:
        ordering = ['name']
        verbose_name = _('permission')
        verbose_name_plural = _('permissions')

    def __str__(self):
        return self.name

    @property
    def can_view(self):
        return 'view' in self.actions

    @property
    def can_add(self):
        return 'add' in self.actions

    @property
    def can_change(self):
        return 'change' in self.actions

    @property
    def can_delete(self):
        return 'delete' in self.actions

    def list_constraints(self):
        """
        Return all constraint sets as a list (even if only a single set is defined).
        """
        if type(self.constraints) is not list:
            return [self.constraints]
        return self.constraints

    def get_absolute_url(self):
        return reverse('users:objectpermission', args=[self.pk])
