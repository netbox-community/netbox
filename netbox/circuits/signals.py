from dcim.utils import rebuild_paths

# ──────────────────────────────────────────────────────────────────────
# Dispatched by GraphRegistry (netbox/graphs.py).
# ──────────────────────────────────────────────────────────────────────


def rebuild_cablepaths(instance, raw=False, **kwargs):
    """
    Rebuild any CablePaths which traverse the peer CircuitTermination.
    """
    if not raw:
        peer_termination = instance.get_peer_termination()
        if peer_termination:
            rebuild_paths([peer_termination])
