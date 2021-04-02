from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from dcim.signals import rebuild_paths
from .models import Circuit, CircuitTermination


@receiver(post_save, sender=CircuitTermination)
def update_circuit(instance, **kwargs):
    """
    When a CircuitTermination has been modified, update its parent Circuit.
    """
    fields = {
        'last_updated': timezone.now(),
        f'termination_{instance.term_side.lower()}': instance.pk,
    }
    Circuit.objects.filter(pk=instance.circuit_id).update(**fields)


@receiver((post_save, post_delete), sender=CircuitTermination)
def rebuild_cablepaths(instance, raw=False, **kwargs):
    """
    Rebuild any CablePaths which traverse the peer CircuitTermination.
    """
    if not raw:
        peer_termination = instance.get_peer_termination()
        if peer_termination:
            rebuild_paths(peer_termination)
