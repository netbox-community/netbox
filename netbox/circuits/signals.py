from django.db.models.signals import post_delete, post_save
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


def clear_circuit_termination_pointer(instance, using=None, origin=None, **kwargs):
    """
    Clear the parent Circuit's cached `termination_a`/`termination_z` pointer with a change-logged
    save. on_delete=SET_NULL clears it via a bulk UPDATE, and related_name='+' hides the relation
    from Circuit._meta.related_objects, so neither path records an ObjectChange. (#23134)

    Connected in CircuitsConfig, not here, so that it precedes handle_deleted_object.
    """
    if not instance.term_side:
        return

    # The pointer goes away with the circuit, so a change record for it would be spurious
    if isinstance(origin, Circuit) or getattr(origin, 'model', None) is Circuit:
        return

    # only_if_references matches what on_delete=SET_NULL would have cleared: the in-memory
    # term_side may not be what the pointer actually references
    field_name = f'termination_{instance.term_side.lower()}'
    CircuitTermination._set_circuit_terminations(
        instance.circuit_id, {field_name: None}, using=using, only_if_references=instance.pk
    )
