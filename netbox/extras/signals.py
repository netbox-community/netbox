from __future__ import unicode_literals

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.core.cache import caches

from .models import Webhook


@receiver((post_save, post_delete), sender=Webhook)
def update_webhook_cache(**kwargs):
    """
    When a Webhook has been modified, update the webhook cache.
    """
    cache = caches['default']
    cache.set('webhook_cache', Webhook.objects.all())
