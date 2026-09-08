from django.db.models.signals import post_delete, post_save, pre_delete
from django.dispatch import receiver

from dcim.signals import rebuild_paths

from .models import Circuit, CircuitTermination


@receiver((post_save, post_delete), sender=CircuitTermination)
def rebuild_cablepaths(instance, raw=False, **kwargs):
    """
    Rebuild any CablePaths which traverse the peer CircuitTermination.
    """
    if not raw:
        peer_termination = instance.get_peer_termination()
        if peer_termination:
            rebuild_paths([peer_termination])


@receiver(pre_delete, sender=CircuitTermination)
def clear_circuit_termination_pointer(instance, using=None, origin=None, **kwargs):
    """
    Clear the parent Circuit's cached `termination_a`/`termination_z` pointer with a change-logged
    save. on_delete=SET_NULL clears it via a bulk UPDATE, and related_name='+' hides the relation
    from Circuit._meta.related_objects, so neither path records an ObjectChange. (#23134)
    """
    if not instance.term_side:
        return

    # The pointer goes away with the circuit, so a change record for it would be spurious
    if isinstance(origin, Circuit) or getattr(origin, 'model', None) is Circuit:
        return

    field_name = f'termination_{instance.term_side.lower()}'
    CircuitTermination._set_circuit_terminations(instance.circuit_id, {field_name: None}, using=using)
