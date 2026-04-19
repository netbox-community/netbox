"""
Declarative cascade registrations for wireless models.

Replaces imperative signal handlers in wireless/signals.py.
"""
from netbox.cascades import CascadeMethod, CascadeSpec, CascadeTiming, cascade_registry


# ──────────────────────────────────────────────────────────────────────
# WirelessLink save → set wireless_link on interfaces
# Replaces: update_connected_interfaces signal handler (cascade part)
# Note: cable path creation part will be handled by GraphRegistry.
# ──────────────────────────────────────────────────────────────────────

def _update_wireless_interfaces(instance, **kwargs):
    """When a WirelessLink is saved, set wireless_link on its interfaces."""
    import logging
    logger = logging.getLogger('netbox.wireless.wirelesslink')

    if kwargs.get('raw'):
        logger.debug(f"Skipping endpoint updates for imported wireless link {instance}")
        return

    if instance.interface_a.wireless_link != instance:
        logger.debug(f"Updating interface A for wireless link {instance}")
        instance.interface_a.wireless_link = instance
        instance.interface_a.save()
    if instance.interface_b.cable != instance:
        logger.debug(f"Updating interface B for wireless link {instance}")
        instance.interface_b.wireless_link = instance
        instance.interface_b.save()


cascade_registry.register(
    CascadeSpec(
        source_model='wireless.wirelesslink',
        target_model='dcim.interface',
        method=CascadeMethod.CUSTOM,
        handler=_update_wireless_interfaces,
        skip_on_create=False,
        description='Set wireless_link reference on connected interfaces when WirelessLink is saved',
    ),
)


# ──────────────────────────────────────────────────────────────────────
# WirelessLink delete → nullify wireless_link on interfaces
# Replaces: nullify_connected_interfaces signal handler (cascade part)
# Note: cable path deletion will be handled by GraphRegistry.
# ──────────────────────────────────────────────────────────────────────

def _nullify_wireless_interfaces(instance, **kwargs):
    """When a WirelessLink is deleted, clear wireless_link on its interfaces."""
    import logging
    from dcim.models import Interface

    logger = logging.getLogger('netbox.wireless.wirelesslink')

    if instance.interface_a is not None:
        logger.debug(f"Nullifying interface A for wireless link {instance}")
        Interface.objects.filter(pk=instance.interface_a.pk).update(wireless_link=None)
    if instance.interface_b is not None:
        logger.debug(f"Nullifying interface B for wireless link {instance}")
        Interface.objects.filter(pk=instance.interface_b.pk).update(wireless_link=None)


cascade_registry.register(
    CascadeSpec(
        source_model='wireless.wirelesslink',
        target_model='dcim.interface',
        timing=CascadeTiming.POST_DELETE,
        method=CascadeMethod.CUSTOM,
        handler=_nullify_wireless_interfaces,
        skip_on_create=False,
        description='Clear wireless_link reference on interfaces when WirelessLink is deleted',
    ),
)
