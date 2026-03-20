from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from dcim.signals import rebuild_paths

from .models import CircuitTermination


@receiver((post_save, post_delete), sender=CircuitTermination)
def rebuild_cablepaths(instance, raw=False, **kwargs):
    """
    Rebuild any CablePaths which traverse the peer CircuitTermination.
    """
    if not raw:
        peer_termination = instance.get_peer_termination()
        if peer_termination:
            rebuild_paths([peer_termination])
