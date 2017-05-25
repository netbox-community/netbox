from __future__ import unicode_literals

from django import template


register = template.Library()


@register.filter()
def decryptable_by(secret, user):
    """
    Determine whether a given User is permitted to decrypt a Secret.
    """
    return secret.decryptable_by(user)
