from __future__ import unicode_literals

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Circuit, CircuitTermination


@receiver((post_save, post_delete), sender=CircuitTermination)
def update_circuit(instance, **kwargs):
    """
    When a CircuitTermination has been modified, update the last_updated time of its parent Circuit.
    """
    Circuit.objects.filter(pk=instance.circuit_id).update(last_updated=timezone.now())
