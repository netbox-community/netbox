from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone

from dcim.signals import update_endpoints
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


@receiver(post_save, sender=CircuitTermination)
def update_connected_endpoints(instance, created, **kwargs):
    if created:
        # Update all endpoints affected by this circuit
        endpoints = instance.circuit.get_related_endpoints()
        update_endpoints(endpoints)


@receiver(post_delete, sender=CircuitTermination)
def nullify_connected_endpoints(instance, **kwargs):
    # Update all endpoints affected by this circuit (through the other termination point)
    endpoints = instance.circuit.get_related_endpoints()
    update_endpoints(endpoints)
