import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from dcim.models import Interface
from .models import WirelessLink


#
# Wireless links
#

@receiver(post_save, sender=WirelessLink)
def update_connected_interfaces(instance, raw=False, **kwargs):
    """
    When a WirelessLink is saved, save a reference to it on each connected interface.
    """
    print('update_connected_interfaces')
    logger = logging.getLogger('netbox.wireless.wirelesslink')
    if raw:
        logger.debug(f"Skipping endpoint updates for imported wireless link {instance}")
        return

    if instance.interface_a.wireless_link != instance:
        logger.debug(f"Updating interface A for wireless link {instance}")
        instance.interface_a.wireless_link = instance
        # instance.interface_a._cable_peer = instance.interface_b  # TODO: Rename _cable_peer field
        instance.interface_a.save()
    if instance.interface_b.cable != instance:
        logger.debug(f"Updating interface B for wireless link {instance}")
        instance.interface_b.wireless_link = instance
        # instance.interface_b._cable_peer = instance.interface_a
        instance.interface_b.save()


@receiver(post_delete, sender=WirelessLink)
def nullify_connected_interfaces(instance, **kwargs):
    """
    When a WirelessLink is deleted, update its two connected Interfaces
    """
    print('nullify_connected_interfaces')
    logger = logging.getLogger('netbox.wireless.wirelesslink')

    if instance.interface_a is not None:
        logger.debug(f"Nullifying interface A for wireless link {instance}")
        Interface.objects.filter(pk=instance.interface_a.pk).update(
            wireless_link=None,
            _cable_peer_type=None,
            _cable_peer_id=None
        )
    if instance.interface_b is not None:
        logger.debug(f"Nullifying interface B for wireless link {instance}")
        Interface.objects.filter(pk=instance.interface_b.pk).update(
            wireless_link=None,
            _cable_peer_type=None,
            _cable_peer_id=None
        )
