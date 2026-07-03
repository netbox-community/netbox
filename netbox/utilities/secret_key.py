"""Generate SECRET_KEY values. Import-safe (stdlib only), so it works before Django or a NetBox
configuration exists: backs `netbox secret-key` and the netbox/generate_secret_key.py script."""

import secrets

__all__ = ('SECRET_KEY_CHARSET', 'SECRET_KEY_LENGTH', 'generate_secret_key')

SECRET_KEY_CHARSET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*(-_=+)'
SECRET_KEY_LENGTH = 50


def generate_secret_key():
    """Return a random 50-character string suitable for SECRET_KEY or an API token pepper."""
    return ''.join(secrets.choice(SECRET_KEY_CHARSET) for _ in range(SECRET_KEY_LENGTH))
