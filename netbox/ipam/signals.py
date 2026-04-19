from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Prefix

# ──────────────────────────────────────────────────────────────────────
# Cascade handlers (clear_primary_ip, clear_oob_ip) have been moved
# to ipam/cascades.py as declarative CascadeSpecs.
# ──────────────────────────────────────────────────────────────────────

#
# Prefix hierarchy maintenance
# These will be moved to GraphRegistry in a future phase.
#


def update_parents_children(prefix):
    """
    Update depth on prefix & containing prefixes
    """
    parents = prefix.get_parents(include_self=True).annotate_hierarchy()
    for parent in parents:
        parent._children = parent.hierarchy_children
    Prefix.objects.bulk_update(parents, ['_children'], batch_size=100)


def update_children_depth(prefix):
    """
    Update children count on prefix & contained prefixes
    """
    children = prefix.get_children(include_self=True).annotate_hierarchy()
    for child in children:
        child._depth = child.hierarchy_depth
    Prefix.objects.bulk_update(children, ['_depth'], batch_size=100)


@receiver(post_save, sender=Prefix)
def handle_prefix_saved(instance, created, **kwargs):

    if created or instance.vrf_id != instance._vrf_id or instance.prefix != instance._prefix:

        update_parents_children(instance)
        update_children_depth(instance)

        if not created:
            old_prefix = Prefix(vrf_id=instance._vrf_id, prefix=instance._prefix)
            update_parents_children(old_prefix)
            update_children_depth(old_prefix)


@receiver(post_delete, sender=Prefix)
def handle_prefix_deleted(instance, **kwargs):

    update_parents_children(instance)
    update_children_depth(instance)
