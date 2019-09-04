from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import Circuit, CircuitTermination


@receiver((post_save, post_delete), sender=CircuitTermination)
def update_circuit(instance, **kwargs):
    """
    When a CircuitTermination has been modified, update the last_updated time of its parent Circuit.
    """
    circuits = Circuit.objects.filter(pk=instance.circuit_id)
    time = timezone.now()
    for circuit in circuits:
        circuit.last_updated = time
        circuit.save()
