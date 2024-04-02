from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from netbox.config import get_config
from utilities.data import flatten_dict

__all__ = (
    'UserConfig',
)


class UserConfig(models.Model):
    """
    This model stores arbitrary user-specific preferences in a JSON data structure.
    """
    user = models.OneToOneField(
        to=get_user_model(),
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
