"""
Connects the global search cache's post_save/post_delete receivers.

Wired explicitly from CoreConfig.ready() (core/apps.py) rather than as a side effect of this
module being imported, so connection happens deterministically at startup instead of depending
on which of this subsystem's several consumers (netbox.forms.search, netbox.views.misc,
extras.management.commands.reindex, netbox.search.jobs, core.jobs, dcim.signals) happens to
import netbox.search first.
"""
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .backends import search_backend


@receiver(post_save)
def caching_handler(sender, instance, created, **kwargs):
    """
    Update the search cache when an object is created or modified. Delegates to whichever
    backend is configured; see SearchBackend.caching_handler().
    """
    search_backend.caching_handler(sender, instance, created=created, **kwargs)


@receiver(post_delete)
def removal_handler(sender, instance, **kwargs):
    """
    Remove an object's cached representation when it is deleted. Delegates to whichever
    backend is configured; see SearchBackend.removal_handler().
    """
    search_backend.removal_handler(sender, instance, **kwargs)
